import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Dict
from app.db.repository_plant import PlantRepository
from app.db.repository_interaction import InteractionRepository
import nltk
from nltk.corpus import stopwords
import pickle
from pathlib import Path

nltk.download('stopwords')
stop_words_es = stopwords.words('spanish')

class RecommendationService:
    def __init__(self, model_path: str = "recommendation_model"):
        self.model_path = Path(model_path)
        self.plants_df = None
        self.cosine_sim_matrix = None
        self.tfidf_vectorizer = None
        self.indexes = None
        self.is_ready = None
        self.model_path.mkdir(parents=True, exist_ok=True)

    def _get_model_files(self):
        """Devuelve las rutas de los archivos del modelo."""
        return {
            "vectorizer": self.model_path / "tfidf_vectorizer.pkl",
            "matrix": self.model_path / "cosine_sim_matrix.pkl",
            "indexes": self.model_path / "indexes.pkl",
            "dataframe": self.model_path / "plants_df.pkl"
        }

    async def train_and_save_model(self):
        """
            Loads data from the database and pre-calculates the similarity matrix.
            This is an 'async' function to use the asynchronous MongoDB driver.
        """

        print("Training and saving new recommendation model...")
        plants_list = await PlantRepository().get_all_verified_plants()
        if not plants_list:
            print('No verified plants found. Aborting training.')
            return    
            
        data_in_dicts = [plant.model_dump() for plant in plants_list]
        self.plants_df = pd.DataFrame(data_in_dicts)
        self.plants_df['id'] = self.plants_df['id'].astype(str)
        
        self.indexes = pd.Series(self.plants_df.index, index=self.plants_df['id'])      

        def join_list_or_empty(field):
            if isinstance(field, list):
                return ' '.join(field)
            return ''

        self.plants_df['content'] = (
            self.plants_df['common_names'].apply(join_list_or_empty) + ' ' +
            self.plants_df['scientific_name'].fillna('') + ' ' +
            self.plants_df['habitat_description'].fillna('') + ' ' +
            self.plants_df['general_ailments'].fillna('') + ' ' +
            self.plants_df['specific_diseases'].apply(join_list_or_empty)
        )

        self.tfidf_vectorizer = TfidfVectorizer(stop_words=stop_words_es)
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.plants_df['content'])

        self.cosine_sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        self.is_ready = True

        files = self._get_model_files()
        with open(files["vectorizer"], "wb") as f:
            pickle.dump(self.tfidf_vectorizer, f)
        with open(files["matrix"], "wb") as f:
            pickle.dump(self.cosine_sim_matrix, f)
        with open(files["indexes"], "wb") as f:
            pickle.dump(self.indexes, f)
        with open(files["dataframe"], "wb") as f:
            pickle.dump(self.plants_df, f)
        print("✅ Modelo de recomendación cargado y listo.")

    def load_model_from_disk(self):
        """
        Esta función carga el modelo pre-calculado desde los archivos.
        Es súper rápida y es lo que tu app de FastAPI usará al arrancar.
        """
        print("Loading pre-trained model from disk...")
        files = self._get_model_files()
        
        try:
            with open(files["vectorizer"], "rb") as f:
                self.tfidf_vectorizer = pickle.load(f)
            with open(files["matrix"], "rb") as f:
                self.cosine_sim_matrix = pickle.load(f)
            with open(files["indexes"], "rb") as f:
                self.indexes = pickle.load(f)
            with open(files["dataframe"], "rb") as f:
                self.plants_df = pickle.load(f)
            
            self.is_ready = True
            print("✅ Recommendation model loaded and ready.")
        except FileNotFoundError:
            print("🚨 Model files not found. Please train the model first.")
            self.is_ready = False

    async def get_recommendations(self, user_id: str, top_n: int = 10) -> List[str]:
        """
        """
        
        if not self.is_ready:
            raise RuntimeError("El servicio de recomendación no está listo.")
        
        interactions_pointer = await InteractionRepository().get_interactions_by_user(user_id)

        data_in_dicts = [plant.model_dump() for plant in interactions_pointer]
        viewed_plant_ids = [str(interaction['plant_id']) for interaction in data_in_dicts]
        
        if not viewed_plant_ids:
            return await InteractionRepository().get_most_viewed_plants(limit=top_n)
        
        all_recommendations: Dict[str, float] = {}
        for plant_id in viewed_plant_ids:
            if plant_id not in self.indexes:
                continue

            idx = self.indexes[plant_id]
            sim_scores = list(enumerate(self.cosine_sim_matrix[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:11]

            for i, score in sim_scores:
                recommended_plant_id = self.plants_df['id'].iloc[i]
                if recommended_plant_id not in all_recommendations:
                    all_recommendations[recommended_plant_id] = 0
                all_recommendations[recommended_plant_id] += score
        
        for viewed_id in viewed_plant_ids:
            all_recommendations.pop(viewed_id, None)

        sorted_recs = sorted(all_recommendations.items(), key=lambda item: item[1], reverse=True)
        aux_rec = [rec[0] for rec in sorted_recs[:top_n]]
        result_plants = []
        for record in aux_rec:
            aux = await PlantRepository().get_plant_by_id(record)
            result_plants.append(aux.model_dump())
        return result_plants
    
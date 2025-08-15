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

# nltk.download('stopwords')
stop_words_es = stopwords.words('spanish')

class RecommendationService:
    def __init__(self):
        self.plants_df = None
        self.cosine_sim_matrix = None
        self.indexes = None
        self.is_ready = None
        
    async def load_model(self):
        """
            Loads data from the database and pre-calculates the similarity matrix.
            This is an 'async' function to use the asynchronous MongoDB driver.
        """

        print("Loading Recommendation Model...")
        plants_list = await PlantRepository().get_all_plants()
        if not plants_list:
            print('Plants not found in the database. Please check the connection.')
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

        tfidf = TfidfVectorizer(stop_words=stop_words_es)
        tfidf_matrix = tfidf.fit_transform(self.plants_df['content'])

        self.cosine_sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        self.is_ready = True
        print("✅ Modelo de recomendación cargado y listo.")

    async def get_recommendations(self, user_id: str, top_n: int = 10) -> List[str]:
        """
        """
        
        if not self.is_ready:
            raise RuntimeError("El servicio de recomendación no está listo.")
        
        interactions_pointer = await InteractionRepository().get_interactions_by_user(user_id)

        data_in_dicts = [plant.model_dump() for plant in interactions_pointer]
        viewed_plant_ids = [str(interaction['plant_id']) for interaction in data_in_dicts]

        if not viewed_plant_ids:
            return []

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
            result_plants.append(aux.model_dump().get('scientific_name'))
        return result_plants
    

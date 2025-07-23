import os
import io
import re
import random
import requests

from huggingface_hub import InferenceClient
from PIL import Image


class PromptEnchancements:

    def enhance_prompt(self, basic_prompt: str, enhancements: dict[str, str]):
        core_concept = basic_prompt.strip().lower()

        category = None
        for categ in enhancements.keys():
            if categ in core_concept or any(word in core_concept for word in [f"{categ}", f"{categ}ed"]):
                category = categ
                break

        if not category:
            category = "general"
            enhancements["general"] = "high detail, professional photography, beautiful composition, 8k quality, realistic"
        
        enhanced = f"{basic_prompt}, {enhancements[category]}"
        negative_prompt = "low quality, blurry, distorted, disfigured, poorly drawn, bad anatomy, watermark, signature, text"

        return enhanced, negative_prompt
    


    def sanitize_prompt(self, prompt):
        """Clean up and fix common prompt issues"""
        prompt = re.sub(r'[!?,.]+ ?', '. ', prompt)
        prompt = re.sub(r'\s+', ' ', prompt).strip()
            
        prompt = prompt.lower()
            
        return prompt
    


    def generate_optimized_image(self, user_prompt, enhancements, width=384, height=384):

        API_TOKEN=os.getenv("HUGGING_FACE_API_TOKEN_GV")
        print(f'API_TOKEN: {API_TOKEN}')
        enhanced_prompt, negative_prompt = self.enhance_prompt(user_prompt, enhancements)

        seed = random.randint(0, 100000)

        client = InferenceClient(
            provider="hf-inference",
            api_key=API_TOKEN,
        )

        image = client.text_to_image(
            prompt=enhanced_prompt,
            width=width,
            height=height,
            negative_prompt=negative_prompt,
            seed=seed,
            model="black-forest-labs/FLUX.1-schnell",
        )

        return image
    


    



class EnchancementsProperties:
    ECHANCEMENTS = {
        "landscape": "detailed landscape, panoramic view, golden hour lighting, atmospheric, high detail, 8k, professional photography",
        "portrait": "detailed portrait, soft lighting, shallow depth of field, studio quality, professional photography, high detail, 8k",
        "animal": "detailed animal photography, telephoto lens, natural habitat, national geographic style, high detail, 8k",
        "food": "food photography, studio lighting, shallow depth of field, mouth-watering, professional food styling, high detail",
        "abstract": "abstract art, vibrant colors, detailed textures, artistic composition, trending on artstation, high detail",
        "building": "architectural photography, golden hour, professional photography, high detail, perfect composition, 8k",
        "vehicle": "professional automotive photography, studio lighting, wide-angle lens, detailed, high quality, 8k",
        # Add more categories as needed
    }

    STYLE_PREFERENCE = {
        "realistic": "photorealistic, detailed, professional photography",
        "cartoon": "cartoon style, vibrant colors, disney pixar style",
        "anime": "anime style, colorful, detailed, studio ghibli inspired",
        "painting": "oil painting, detailed brushwork, professional art",
        "sketch": "pencil sketch, detailed, black and white, professional drawing"
    }
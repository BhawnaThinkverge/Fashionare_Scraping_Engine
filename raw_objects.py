import pandas as pd
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
import json
import os
from google import genai
import re
import glob

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def extract_fashion_data(article):
    prompt = f"""
You are a fashion trend extraction system.
Extract structured information from this fashion article.

Return only Valid JSON.
No Markdown.
No Explanation.

Article:
{article}

Schema:

{{
"raw_type": "",
"group": "",
"extracted_attributes": {{}},
"demand_direction": "",
"raw_text": ""
}}

Allowed raw_type:
product, search_term, hasgtag, palette, editorial, brand

Allowed_group:
color, silhoutte, pattern, material, item_style, aesthetic, brand

For color:
{{
"color": "",
"hex": "NA",
"color_family": "",
"finish": "",
"palette_role": "",
"pairings": [],
"season": "",
"keywords": []
}}

For silhouette:
{{
"silhouette": "",
"fit": "",
"volume": "",
"length": "",
"applies_to": "",
"season": "",
"keywords": []
}}

For pattern:
{{
"pattern": "",
"pattern_family": "",
"scale": "",
"colorway": [],
"placement": "",
"season": "",
"keywords": []
}}

For material:
{{
"material": "",
"material_family": "",
"texture": "",
"finish": "",
"weight": "",
"season": "",
"keywords": []
}}

For item_style:
{{
"product_type": "",
"category": "",
"key_features": [],
"gender": "",
"season": "",
"keywords": []
}}

For aesthetic:
{{
"style": "",
"mood": "",
"associated_items": [],
"associated_colors": [],
"consumer_segment": "",
"season": "",
"keywords": []
}}

For brand:
{{
"brand": "",
"rank": "",
"movement": "",
"ranking_list": "",
"associated_products": [],
"associated_aesthetic": "",
"season": "",
"keywords": []
}}

"""
       
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        result = response.text
            

        if not result:
            return None

        result = result.replace("```json","")
        result = result.replace("```","")
        result = result.strip()

        decoder = json.JSONDecoder()

        objects = []

        text = result

        while text:
            try:
                obj, index = decoder.raw_decode(text)
                objects.append(obj)

                text = text[index:].strip()

            except json.JSONDecodeError:
                break

        if len(objects) == 1:
            return objects[0]

        elif len(objects) > 1:
            return objects

        return None

    except Exception as e:
        print("Extraction failed", e)
        return None
       

final_rows = []

os.makedirs("scraped_data", exist_ok=True)

files = glob.glob("scraped_data/*.xlsx")

for file in files:
    print(f"Processing file: {file}")

    df = pd.read_excel(file)

    final_rows = []

    source_name = os.path.basename(file)
    source_name = source_name.replace("_Fashion_Data.xlsx", "")
    source_name = source_name.lower()

    for index, row in df.iterrows():
        article = row.get("Full Article", "")
        if pd.isna(article) or article == "":
            continue

        print(f"Processing article {index}")
        article = article[:5000]
        extracted = extract_fashion_data(article)

        if extracted is None:
            print("Skipping article", index)
            continue

        if isinstance(extracted, list):
            if len(extracted) == 0:
                continue

            extracted = extracted[0]

        observation = {
            "observation_id": str(uuid.uuid4()),
            "source": source_name,
            "source_url": row.get("URL", ""),
            "captured_date": datetime.now(timezone.utc).isoformat(),
            "raw_type": extracted.get("raw_type", "unknown"),
            "group": extracted.get("group", "unknown"),
            "extracted_attributes": extracted.get("extracted_attributes", "NA"),
            "demand_direction": extracted.get("demand_direction", "unknown"),
            "raw_text": extracted.get("raw_text", "")
            
        }

        row["observation"] = json.dumps(
            observation,
            ensure_ascii=False
        )


        final_rows.append(row)

    final = pd.DataFrame(final_rows)

    output_file = file.replace(
        "_Fashion_Data.xlsx",
        "_Trend_Data.xlsx"

    )

    final.to_excel(
        output_file,
        index=False
    )

    print(f"Saved: {output_file}")

print("All files are saved")

    



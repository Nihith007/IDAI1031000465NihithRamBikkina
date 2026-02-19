# IDAI1031000465-Nihith-Ram-Bikkina

# AI-powered virtual sports coach for youth athletes

# Candidate Name - Nihith Ram Bikkina

# Candidate Registration Number - 1000465

# CRS Name: Artificial Intelligence

# Course Name - Generative AI

# School name - Birla Open Minds International School, Kollur

# Summative Assessment 

**Project Overview**

This project is an AI-powered web application designed to deliver personalized fitness coaching for athletes. Built using Streamlit and integrated with the Gemini API, the platform generates customized training schedules, injury-conscious recovery routines, tactical performance advice, and nutrition guidance. By analyzing inputs such as the athlete’s sport, playing position, injury history, and fitness goals, the system aims to provide safe, structured, and accessible coaching—particularly for young athletes who lack access to professional trainers.

**Problem Statement**

Many young athletes follow generic or self-designed training programs without expert supervision. This often leads to inefficient workouts, slow performance improvement, and an increased likelihood of injury due to poor recovery and overload. This project addresses these issues by using Generative AI to create adaptive, personalized, and safety-focused training recommendations tailored to the unique requirements of each athlete.

**Objectives**

* Develop a web-based fitness coaching platform powered by Generative AI
* Generate individualized workout and recovery plans based on user inputs
* Incorporate injury-aware logic to reduce training risks
* Offer tactical insights to enhance sport-specific performance
* Provide basic nutrition and hydration recommendations
* Deploy the system using Streamlit with seamless Gemini API integration

**Research Summary**

The development process included studying sport-specific training methodologies, injury prevention techniques, recovery protocols, and existing AI-driven fitness systems. Research on the application of artificial intelligence in sports coaching influenced the overall system design. The final application emphasizes personalization, adaptability, and athlete safety, making it suitable for young and developing athletes.

**Model Configuration**

* Different slider settings were used to optimize response quality:
* A low creativity (0.3) was selected for generating structured, consistent, and safety-oriented workout and recovery plans.
* A higher creativity (0.7) was used for more creative outputs, including tactical strategies and nutrition suggestions.
* Prompt engineering was iteratively refined through testing to improve relevance, clarity, and personalization of responses.

**Sample Outputs and Validation**

The system was tested across multiple sports, playing roles, and injury scenarios to evaluate accuracy and safety. Generated outputs were assessed for relevance, personalization, and injury awareness. Recovery-focused prompts appropriately adjusted training intensity, while workout plans aligned well with sport-specific demands. Continuous tuning of prompts and parameters further improved output quality and effectiveness.

**Web Application Features**

* User input fields for sport, position, injury history, and fitness goals
* AI-generated personalized training and recovery programs
* Injury-sensitive exercise recommendations
* Tactical performance enhancement tips
* Nutrition and hydration guidance
* A clean, intuitive, and user-friendly interface

**Deployment**

The application was built with Streamlit and integrated with the Gemini API to generate AI-driven responses. The complete project was hosted on GitHub and deployed on Streamlit Cloud, allowing public access to the web application.

* Open Google AI Studio and sign in with a Google account.
* Go to API keys / Get API key and click Create API key.
* Select or create a Google Cloud project and copy the generated Gemini API key.
* Open your Streamlit app code and configure the Gemini client using st.secrets["GEMINI_API_KEY"] instead of hardcoding the key.
* Upload the project files to GitHub, ensuring no API keys are included in the repository.
* Log in to Streamlit Cloud and deploy the app by selecting the repository, branch, and main file.
* After deployment, open the app settings in Streamlit Cloud and go to Secrets.
* Add GEMINI_API_KEY = "your_api_key_here" in the secrets section and save.
* Restart or refresh the app to apply the secret.
* Test the application to confirm that AI-generated responses are working correctly.

**Live app link:** https://coachbot-nihith-ram-bikkina-tysqbrnpj8yu59v96zjkqo.streamlit.app/
# Screenshots

<img width="297" height="209" alt="image" src="https://github.com/user-attachments/assets/97be7c1e-6a8f-41db-a147-2db2ca11410c" />

<img width="306" height="470" alt="image" src="https://github.com/user-attachments/assets/8a8796fb-10ec-498a-84c5-63d055e73608" />

<img width="302" height="284" alt="image" src="https://github.com/user-attachments/assets/c05592eb-f57a-40e0-9bf4-f4e77472f88a" />

<img width="299" height="332" alt="image" src="https://github.com/user-attachments/assets/db6b1799-643d-419f-8c99-93f16565d075" />

<img width="299" height="402" alt="image" src="https://github.com/user-attachments/assets/4215ec16-2878-457b-b148-232742bc3d27" />

<img width="1456" height="850" alt="image" src="https://github.com/user-attachments/assets/800bd889-5537-48e9-a5e6-369c66d1c112" />

<img width="1360" height="315" alt="image" src="https://github.com/user-attachments/assets/673b6e1d-b91b-4705-955b-4c9f9ac9a799" />

<img width="1416" height="797" alt="image" src="https://github.com/user-attachments/assets/4789885b-b411-4f88-a901-ee7b1c93b736" />

# Example Prompts

Design a strength and conditioning program for a 16-year-old midfielder playing football.

<img width="1455" height="885" alt="image" src="https://github.com/user-attachments/assets/0801bcc0-3512-465f-8371-4414b3afa6fa" />

Create a beginner-to-advanced training progression plan for an athlete in basketball.

<img width="1480" height="740" alt="image" src="https://github.com/user-attachments/assets/23a58719-0417-4d32-ba1a-86f8c945e255" />

Suggest low-impact workouts to maintain fitness while recovering from an ankle sprain.

<img width="1387" height="891" alt="image" src="https://github.com/user-attachments/assets/451a6460-16ab-4428-9d8a-98e375c810d2" />

Provide match-day preparation tips for a striker in football.

<img width="1442" height="783" alt="image" src="https://github.com/user-attachments/assets/b627c615-cc7c-4787-b568-feddd874c424" />

Generate a flexibility and mobility routine tailored for swimming.

<img width="1392" height="599" alt="image" src="https://github.com/user-attachments/assets/e8fb6dfb-a442-40cf-b9f7-86015ac6adae" />

Create a weekly endurance training plan for a long-distance runner in athletics.

<img width="1431" height="843" alt="image" src="https://github.com/user-attachments/assets/b7dd7574-4cac-4035-99f7-9bd168f895de" />

Suggest injury-prevention exercises commonly needed for cricket players.

<img width="1433" height="870" alt="image" src="https://github.com/user-attachments/assets/a500756e-8e9e-4cfc-9d48-208194a0dc72" />

Provide age-appropriate nutrition tips for a 15-year-old athlete training for tennis.

<img width="1444" height="749" alt="image" src="https://github.com/user-attachments/assets/4c58dd1f-39bb-4f52-b34c-faa5154ffe9d" />

Generate a home-based workout plan for athletes who play badminton without gym equipment.

<img width="1509" height="804" alt="image" src="https://github.com/user-attachments/assets/eb66b4e0-1548-4861-83bc-1bd79bfe2c68" />

Create a post-training recovery routine including stretching and rest tips for volleyball players.

<img width="1471" height="857" alt="image" src="https://github.com/user-attachments/assets/75a3b0aa-52b2-45e6-8c29-fdf506882e59" />










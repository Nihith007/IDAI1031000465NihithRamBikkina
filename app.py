"""
Smart Fitness CoachBot - AI-Powered Personal Training Assistant
"""

import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="CoachBot AI - Your Personal Fitness Coach",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #1E88E5;
    }
    .output-box {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px solid #1E88E5;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'api_key_configured' not in st.session_state:
    st.session_state.api_key_configured = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ============================================================================
# TABULAR FORMATTING FUNCTIONS
# ============================================================================

def create_weekly_training_table(training_days=None):
    """Create a table showing weekly training schedule"""
    
    if training_days is None:
        training_days = {
            'Monday': {'Intensity': 8, 'Focus': 'Strength Training', 'Duration': '60 min'},
            'Tuesday': {'Intensity': 6, 'Focus': 'Cardio/Endurance', 'Duration': '45 min'},
            'Wednesday': {'Intensity': 9, 'Focus': 'Sport-Specific Skills', 'Duration': '75 min'},
            'Thursday': {'Intensity': 5, 'Focus': 'Recovery/Mobility', 'Duration': '30 min'},
            'Friday': {'Intensity': 7, 'Focus': 'Strength + Conditioning', 'Duration': '60 min'},
            'Saturday': {'Intensity': 4, 'Focus': 'Light Cardio', 'Duration': '30 min'},
            'Sunday': {'Intensity': 2, 'Focus': 'Rest/Active Recovery', 'Duration': '20 min'}
        }
    
    df = pd.DataFrame.from_dict(training_days, orient='index')
    df.index.name = 'Day'
    df.reset_index(inplace=True)
    
    return df

def create_training_distribution_table(training_types=None):
    """Create a table showing training type distribution"""
    
    if training_types is None:
        training_types = {
            'Strength Training': 30,
            'Cardio/Endurance': 25,
            'Skill Work': 25,
            'Flexibility/Mobility': 10,
            'Rest/Recovery': 10
        }
    
    df = pd.DataFrame(list(training_types.items()), columns=['Training Type', 'Percentage (%)'])
    df['Hours per Week'] = (df['Percentage (%)'] / 100 * 10).round(1)  # Assuming 10 hours/week
    
    return df

def create_nutrition_table(calorie_goal='Maintenance'):
    """Create a nutrition breakdown table"""
    
    data = {
        'Nutrient': ['Protein', 'Carbohydrates', 'Fats', 'Total Calories'],
        'Percentage': ['30%', '45%', '25%', '100%'],
        'Grams per Day': ['150g', '280g', '70g', '-'],
        'Calories': ['600 kcal', '1120 kcal', '630 kcal', '2350 kcal']
    }
    
    df = pd.DataFrame(data)
    return df

def create_weekly_meal_plan_table():
    """Create a sample weekly meal plan table"""
    
    meals = {
        'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'Breakfast': ['Oatmeal + Eggs', 'Greek Yogurt + Fruits', 'Whole Grain Toast + Avocado', 
                     'Protein Smoothie', 'Scrambled Eggs + Veggies', 'Pancakes + Berries', 'Omelet + Toast'],
        'Lunch': ['Chicken + Rice + Veggies', 'Fish + Quinoa Salad', 'Turkey Wrap + Soup',
                 'Pasta + Lean Meat', 'Grilled Chicken Salad', 'Rice Bowl + Protein', 'Sandwich + Fruit'],
        'Dinner': ['Salmon + Sweet Potato', 'Lean Beef + Brown Rice', 'Chicken Stir-fry',
                  'Fish + Vegetables', 'Turkey + Quinoa', 'Grilled Chicken + Pasta', 'Lean Meat + Rice'],
        'Snacks': ['Protein Bar + Nuts', 'Fruit + Cheese', 'Hummus + Veggies',
                  'Greek Yogurt', 'Trail Mix', 'Protein Shake', 'Fruit + Nut Butter']
    }
    
    df = pd.DataFrame(meals)
    return df

def create_exercise_table(exercises=None):
    """Create an exercise routine table"""
    
    if exercises is None:
        exercises = {
            'Exercise': ['Squats', 'Bench Press', 'Deadlifts', 'Pull-ups', 'Shoulder Press', 
                        'Lunges', 'Rows', 'Core Work'],
            'Sets': [4, 4, 3, 3, 3, 3, 4, 3],
            'Reps': ['8-10', '8-10', '6-8', '8-12', '10-12', '10 each leg', '10-12', '15-20'],
            'Rest (sec)': [90, 90, 120, 90, 60, 60, 75, 45],
            'Notes': ['Focus on form', 'Control the weight', 'Keep back straight', 
                     'Use assistance if needed', 'Full range of motion', 'Maintain balance',
                     'Squeeze at top', 'Engage core throughout']
        }
    
    df = pd.DataFrame(exercises)
    return df

def create_progress_tracking_table(weeks=8):
    """Create a progress tracking table"""
    
    data = {
        'Week': list(range(1, weeks + 1)),
        'Strength (%)': [20, 30, 42, 55, 65, 75, 82, 90][:weeks],
        'Endurance (%)': [25, 35, 45, 58, 68, 76, 84, 92][:weeks],
        'Skill Level (%)': [30, 38, 48, 58, 68, 76, 83, 89][:weeks],
        'Body Weight (kg)': [70, 70.5, 71, 71.2, 71.5, 71.8, 72, 72.2][:weeks],
        'Notes': ['Baseline', 'Good progress', 'Increasing intensity', 'Maintaining form',
                 'Peak week', 'Recovery focus', 'Final push', 'Assessment week'][:weeks]
    }
    
    df = pd.DataFrame(data)
    return df

def create_injury_recovery_table():
    """Create an injury recovery timeline table"""
    
    data = {
        'Phase': ['Week 1-2', 'Week 3-4', 'Week 5-6', 'Week 7-8', 'Week 9+'],
        'Focus': ['Pain Management', 'Gentle Movement', 'Strength Building', 
                 'Sport-Specific Work', 'Full Training'],
        'Intensity': ['Very Low (2-3/10)', 'Low (3-4/10)', 'Moderate (5-6/10)', 
                     'High (7-8/10)', 'Full (9-10/10)'],
        'Activities': ['Ice, Rest, Gentle Stretching', 'Pool Work, Light Mobility', 
                      'Resistance Bands, Bodyweight', 'Light Sport Drills', 'Full Practice'],
        'Red Flags': ['Sharp pain, Swelling', 'Persistent pain', 'Limited ROM',
                     'Pain during sport moves', 'Recurring issues']
    }
    
    df = pd.DataFrame(data)
    return df

def display_tabular_dashboard(feature_type, training_frequency, training_duration):
    """Display training data in tabular format"""
    
    st.markdown("---")
    st.markdown("## 📊 Training Schedule & Breakdown (Tables)")
    st.markdown("*Organized data for easy tracking and reference*")
    
    # ALWAYS show weekly training schedule
    st.markdown("### 📅 Weekly Training Schedule")
    weekly_table = create_weekly_training_table()
    st.dataframe(weekly_table, use_container_width=True, hide_index=True)
    
    # Show feature-specific tables
    if "Workout" in feature_type or "Training" in feature_type or "Strength" in feature_type:
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💪 Exercise Routine")
            exercise_table = create_exercise_table()
            st.dataframe(exercise_table, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 📈 Training Distribution")
            distribution_table = create_training_distribution_table()
            st.dataframe(distribution_table, use_container_width=True, hide_index=True)
        
        st.markdown("### 📊 8-Week Progress Tracking")
        progress_table = create_progress_tracking_table(8)
        st.dataframe(progress_table, use_container_width=True, hide_index=True)
    
    elif "Nutrition" in feature_type:
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🍽️ Macro Breakdown")
            nutrition_table = create_nutrition_table()
            st.dataframe(nutrition_table, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 📋 Training Distribution")
            meal_dist = {
                'Breakfast': 25,
                'Lunch': 30,
                'Dinner': 30,
                'Snacks': 15
            }
            meal_table = pd.DataFrame(list(meal_dist.items()), 
                                     columns=['Meal', 'Calorie %'])
            st.dataframe(meal_table, use_container_width=True, hide_index=True)
        
        st.markdown("### 🗓️ Weekly Meal Plan")
        meal_plan_table = create_weekly_meal_plan_table()
        st.dataframe(meal_plan_table, use_container_width=True, hide_index=True)
    
    elif "Recovery" in feature_type or "Mobility" in feature_type:
        
        st.markdown("### 🏥 Recovery Timeline")
        recovery_table = create_injury_recovery_table()
        st.dataframe(recovery_table, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🧘 Recovery Activities")
            recovery_types = {
                'Stretching': 30,
                'Foam Rolling': 20,
                'Low Impact Cardio': 25,
                'Rest': 25
            }
            recovery_dist = pd.DataFrame(list(recovery_types.items()), 
                                        columns=['Activity', 'Time %'])
            st.dataframe(recovery_dist, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 📊 Progress Tracking")
            progress_table = create_progress_tracking_table(8)
            st.dataframe(progress_table[['Week', 'Strength (%)', 'Endurance (%)']],
                        use_container_width=True, hide_index=True)
    
    elif "Endurance" in feature_type or "Speed" in feature_type:
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏃 Training Types")
            training_types = {
                'Interval Training': 35,
                'Long Distance': 30,
                'Speed Work': 20,
                'Recovery Runs': 15
            }
            training_dist = pd.DataFrame(list(training_types.items()),
                                        columns=['Type', 'Percentage %'])
            st.dataframe(training_dist, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 📈 Training Distribution")
            distribution_table = create_training_distribution_table(training_types)
            st.dataframe(distribution_table, use_container_width=True, hide_index=True)
        
        st.markdown("### 📊 12-Week Progress Plan")
        progress_table = create_progress_tracking_table(12)
        st.dataframe(progress_table, use_container_width=True, hide_index=True)
    
    else:
        # Default tables for other features
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Training Distribution")
            default_types = {
                'Physical Training': 40,
                'Skill Development': 30,
                'Mental Training': 15,
                'Recovery': 15
            }
            default_dist = pd.DataFrame(list(default_types.items()),
                                       columns=['Category', 'Percentage %'])
            st.dataframe(default_dist, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 📊 Progress Tracking")
            progress_table = create_progress_tracking_table(8)
            st.dataframe(progress_table[['Week', 'Strength (%)', 'Skill Level (%)']],
                        use_container_width=True, hide_index=True)

# Header
st.markdown('<h1 class="main-header">🏋️ CoachBot AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your Personal AI Fitness & Sports Coach - Powered by Gemini 2.5 Flash</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #1E88E5; font-weight: 500;">✨ Now with Organized Training Tables & Data ✨</p>', unsafe_allow_html=True)

# Sidebar for API Key and User Profile
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key from Streamlit Secrets or Input
    api_key = None
    
    
    # User Profile Section
    st.header("👤 Your Profile")
    
    user_name = st.text_input("Name", placeholder="John Doe")
    user_age = st.number_input("Age", min_value=10, max_value=100, value=15)
    user_gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
    
    st.markdown("---")
    
    # Sport Selection
    st.header("⚽ Sport Details")
    sport = st.selectbox(
        "Select Your Sport",
        ["Football/Soccer", "Cricket", "Basketball", "Athletics/Track & Field", 
         "Tennis", "Swimming", "Volleyball", "Badminton", "Hockey", "Other"]
    )
    
    # Position based on sport
    position_options = {
        "Football/Soccer": ["Goalkeeper", "Defender", "Midfielder", "Forward/Striker", "Winger"],
        "Cricket": ["Batsman", "Bowler (Fast)", "Bowler (Spin)", "All-rounder", "Wicket-keeper"],
        "Basketball": ["Point Guard", "Shooting Guard", "Small Forward", "Power Forward", "Center"],
        "Athletics/Track & Field": ["Sprinter", "Middle Distance", "Long Distance", "Jumper", "Thrower"],
        "Tennis": ["Singles Player", "Doubles Player", "Baseline Player", "Serve-and-Volley"],
        "Swimming": ["Freestyle", "Backstroke", "Breaststroke", "Butterfly", "Individual Medley"],
        "Volleyball": ["Setter", "Outside Hitter", "Middle Blocker", "Libero", "Opposite Hitter"],
        "Badminton": ["Singles Player", "Doubles Player", "Mixed Doubles"],
        "Hockey": ["Forward", "Midfielder", "Defender", "Goalkeeper"],
        "Other": ["General Athlete"]
    }
    
    position = st.selectbox("Player Position", position_options.get(sport, ["General"]))
    
    st.markdown("---")
    
    # Fitness Level & Goals
    st.header("🎯 Fitness Details")
    fitness_level = st.select_slider(
        "Current Fitness Level",
        options=["Beginner", "Intermediate", "Advanced", "Elite"]
    )
    
    injury_history = st.text_area(
        "Injury History/Risk Zones",
        placeholder="e.g., Previous ankle sprain, knee sensitivity, shoulder pain",
        help="Describe any past injuries or areas that need special attention"
    )
    
    st.markdown("---")
    
    # Nutrition Preferences
    st.header("🍽️ Nutrition Preferences")
    diet_type = st.selectbox("Diet Type", ["Vegetarian", "Non-Vegetarian", "Vegan", "Pescatarian"])
    allergies = st.text_input("Allergies/Food Restrictions", placeholder="e.g., Nuts, dairy, gluten")
    calorie_goal = st.select_slider(
        "Daily Calorie Goal",
        options=["Maintenance", "Deficit (Weight Loss)", "Surplus (Muscle Gain)"]
    )

# Main content area
if st.session_state.api_key_configured:
    
    # Feature Selection
    st.header("🎯 What would you like CoachBot to help you with?")
    
    feature = st.selectbox(
        "Select a Feature",
        [
            "1. Full-Body Workout Plan",
            "2. Recovery Training Schedule",
            "3. Tactical Coaching Tips",
            "4. Nutrition Guide (Weekly)",
            "5. Warm-up & Cooldown Routine",
            "6. Mental Focus & Tournament Preparation",
            "7. Hydration & Electrolyte Strategy",
            "8. Pre-Match Visualization Techniques",
            "9. Positional Decision-Making Drills",
            "10. Mobility Workouts (Post-Injury)",
            "11. Strength Training Program",
            "12. Speed & Agility Training",
            "13. Endurance Building Program",
            "14. Match-Day Preparation Plan",
            "15. Custom Question (Ask Anything)"
        ]
    )
    
    # Additional context based on feature
    col1, col2 = st.columns(2)
    
    with col1:
        training_intensity = st.select_slider(
            "Training Intensity",
            options=["Low", "Moderate", "High", "Very High"]
        )
        
        training_duration = st.selectbox(
            "Training Duration per Session",
            ["30 minutes", "45 minutes", "60 minutes", "90 minutes", "120 minutes"]
        )
    
    with col2:
        training_frequency = st.selectbox(
            "Training Frequency",
            ["2-3 times/week", "4-5 times/week", "6 times/week", "Daily"]
        )
        
        specific_goal = st.text_input(
            "Specific Goal",
            placeholder="e.g., Improve stamina, recover from injury, tournament prep"
        )
    
    # Custom question for feature 15
    custom_question = ""
    if "15. Custom Question" in feature:
        custom_question = st.text_area(
            "Ask Your Custom Question",
            placeholder="Type your specific question here...",
            height=100
        )
    
    # Temperature control for AI creativity
    with st.expander("🔧 Advanced Settings (Optional)"):
        temperature = st.slider(
            "AI Creativity Level",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="Lower values give more conservative answers, higher values are more creative"
        )
        
        st.markdown("---")
        st.markdown("**📊 Display Settings**")
        show_charts = st.checkbox("Show Training Tables & Data", value=True, 
                                   help="Display organized tables with your plan")
    
    # Generate button
    if st.button("🚀 Generate Personalized Plan", type="primary"):
        
        # Build the prompt based on selected feature
        user_context = f"""
        User Profile:
        - Name: {user_name if user_name else 'Athlete'}
        - Age: {user_age}
        - Gender: {user_gender}
        - Sport: {sport}
        - Position: {position}
        - Fitness Level: {fitness_level}
        - Injury History: {injury_history if injury_history else 'None'}
        - Diet Type: {diet_type}
        - Allergies: {allergies if allergies else 'None'}
        - Calorie Goal: {calorie_goal}
        - Training Intensity: {training_intensity}
        - Training Duration: {training_duration}
        - Training Frequency: {training_frequency}
        - Specific Goal: {specific_goal if specific_goal else 'General improvement'}
        """
        
        # Prompt templates for each feature
        prompts = {
            "1. Full-Body Workout Plan": f"""
            As an experienced sports coach, create a comprehensive full-body workout plan for a {position} in {sport}.
            
            {user_context}
            
            Please provide:
            1. Detailed workout routine with exercises, sets, and reps
            2. Sport-specific exercises for their position
            3. Safety considerations based on injury history
            4. Progressive overload strategy
            5. Rest and recovery recommendations
            
            Format the response in a clear, structured manner with proper sections.
            """,
            
            "2. Recovery Training Schedule": f"""
            As a sports physiotherapist and coach, create a safe recovery training schedule.
            
            {user_context}
            
            Focus on:
            1. Low-impact exercises suitable for injury recovery
            2. Gradual progression back to full training
            3. Specific exercises to avoid based on injury history
            4. Flexibility and mobility work
            5. Timeline for recovery phases (Week 1, 2, 3, etc.)
            6. Signs to watch for and when to rest
            
            Prioritize safety and long-term health over quick returns.
            """,
            
            "3. Tactical Coaching Tips": f"""
            As a tactical coach specializing in {sport}, provide advanced coaching tips for a {position}.
            
            {user_context}
            
            Include:
            1. Position-specific tactical awareness
            2. Game-reading skills to develop
            3. Decision-making scenarios and solutions
            4. Communication strategies with teammates
            5. Common mistakes to avoid
            6. Training drills to improve tactical understanding
            
            Use examples from professional play where relevant.
            """,
            
            "4. Nutrition Guide (Weekly)": f"""
            As a sports nutritionist, create a comprehensive weekly nutrition guide.
            
            {user_context}
            
            Provide:
            1. Daily meal plans (Breakfast, Lunch, Dinner, Snacks)
            2. Pre-training and post-training nutrition
            3. Macro breakdown (Proteins, Carbs, Fats)
            4. Specific foods to support their sport and position
            5. Timing of meals around training
            6. Hydration recommendations
            7. Supplement suggestions (if appropriate for age)
            
            Consider their dietary restrictions and calorie goals.
            """,
            
            "5. Warm-up & Cooldown Routine": f"""
            Create a personalized warm-up and cooldown routine for a {position} in {sport}.
            
            {user_context}
            
            Include:
            1. Dynamic warm-up (10-15 minutes)
            2. Sport-specific activation drills
            3. Position-specific movement prep
            4. Modifications for injury history
            5. Cooldown and static stretching routine (10-15 minutes)
            6. Foam rolling and mobility work
            
            Make it practical and easy to follow before every training session.
            """,
            
            "6. Mental Focus & Tournament Preparation": f"""
            As a sports psychologist, create a mental preparation program for tournaments.
            
            {user_context}
            
            Cover:
            1. Pre-tournament mental preparation (weeks before)
            2. Day-before and morning-of routines
            3. Visualization techniques specific to their sport
            4. Pressure management strategies
            5. Focus and concentration drills
            6. Dealing with nervousness and anxiety
            7. Post-performance reflection techniques
            
            Make it age-appropriate and practical.
            """,
            
            "7. Hydration & Electrolyte Strategy": f"""
            Design a comprehensive hydration and electrolyte strategy for a young athlete.
            
            {user_context}
            
            Provide:
            1. Daily water intake recommendations
            2. Pre, during, and post-training hydration protocols
            3. Electrolyte balance strategies
            4. Signs of dehydration to watch for
            5. Sport-specific hydration needs
            6. Hydration for different weather conditions
            7. Recommended drinks and timing
            
            Consider their age and training intensity.
            """,
            
            "8. Pre-Match Visualization Techniques": f"""
            Teach effective pre-match visualization techniques for a {position} in {sport}.
            
            {user_context}
            
            Include:
            1. Step-by-step visualization process
            2. What to visualize (successful plays, positioning, etc.)
            3. When to practice visualization
            4. Combining visualization with breathing techniques
            5. Confidence-building mental imagery
            6. Dealing with negative thoughts
            7. Creating a pre-match mental routine
            
            Make it practical for a young athlete to implement.
            """,
            
            "9. Positional Decision-Making Drills": f"""
            Create position-specific decision-making drills for a {position} in {sport}.
            
            {user_context}
            
            Provide:
            1. Situational awareness drills
            2. Quick decision-making exercises
            3. Game-like scenarios to practice
            4. Reading the game drills
            5. Positioning and movement drills
            6. Progressive difficulty levels
            7. How to practice alone and with teammates
            
            Focus on improving their game intelligence.
            """,
            
            "10. Mobility Workouts (Post-Injury)": f"""
            Create a mobility and flexibility program for post-injury recovery.
            
            {user_context}
            
            Include:
            1. Gentle mobility exercises for affected areas
            2. Full-body mobility routine
            3. Dynamic stretching sequences
            4. Yoga-inspired movements for athletes
            5. Frequency and duration recommendations
            6. Progression markers
            7. When to advance to next level
            
            Emphasize safety and gradual progression.
            """,
            
            "11. Strength Training Program": f"""
            Design a sport-specific strength training program for a {position} in {sport}.
            
            {user_context}
            
            Cover:
            1. Position-specific strength requirements
            2. Compound and isolation exercises
            3. Periodization plan (3-month program)
            4. Rep ranges and load progression
            5. Core strength development
            6. Injury prevention exercises
            7. Integration with sport training
            
            Make it safe and effective for their age group.
            """,
            
            "12. Speed & Agility Training": f"""
            Create a comprehensive speed and agility development program for {sport}.
            
            {user_context}
            
            Include:
            1. Acceleration drills
            2. Top-speed development
            3. Change of direction training
            4. Agility ladder work
            5. Plyometric exercises
            6. Sport-specific speed drills
            7. Progression timeline
            
            Consider their position requirements and injury history.
            """,
            
            "13. Endurance Building Program": f"""
            Design an endurance building program for a {position} in {sport}.
            
            {user_context}
            
            Provide:
            1. Aerobic base building
            2. Anaerobic capacity development
            3. Sport-specific conditioning
            4. Interval training protocols
            5. Long-duration training sessions
            6. Active recovery methods
            7. 8-week progression plan
            
            Balance intensity with recovery needs.
            """,
            
            "14. Match-Day Preparation Plan": f"""
            Create a complete match-day preparation plan for a {position} in {sport}.
            
            {user_context}
            
            Cover:
            1. Night-before routine (sleep, nutrition)
            2. Morning-of preparation
            3. Pre-match meal timing and content
            4. Arrival time and pre-game warm-up
            5. Mental preparation sequence
            6. Equipment checklist
            7. Post-match recovery protocol
            
            Make it a comprehensive routine they can follow consistently.
            """,
            
            "15. Custom Question (Ask Anything)": f"""
            As an expert sports coach and fitness advisor, answer the following question:
            
            {custom_question}
            
            Context about the athlete:
            {user_context}
            
            Provide a detailed, personalized response that considers their sport, position, 
            fitness level, and any injury history. Be specific and practical.
            """
        }
        
        selected_prompt = prompts.get(feature, prompts["15. Custom Question (Ask Anything)"])
        
        try:
            # Show loading spinner
            with st.spinner("🤖 CoachBot is creating your personalized plan..."):
                
                # Configure the model
                generation_config = {
                    "temperature": temperature,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
                
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    generation_config=generation_config
                )
                
                # Generate response
                response = model.generate_content(selected_prompt)
                
                # Check if response was blocked or incomplete
                if not response.text:
                    st.error("⚠️ Response was blocked or incomplete. Please try again with a different prompt.")
                    st.stop()
                
                # Display the result
                st.markdown("---")
                st.markdown("## 📋 Your Personalized Plan")
                
                st.markdown('<div class="output-box">', unsafe_allow_html=True)
                st.markdown(response.text)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Display tables if enabled
                if 'show_charts' not in locals() or show_charts:
                    display_tabular_dashboard(feature, training_frequency, training_duration)
                
                # Save to chat history
                st.session_state.chat_history.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "feature": feature,
                    "response": response.text
                })
                
                # Download option
                st.download_button(
                    label="📥 Download Plan as Text File",
                    data=response.text,
                    file_name=f"coachbot_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
                
                st.success("✅ Plan generated successfully! Review it carefully and consult with a coach if needed.")
                
        except Exception as e:
            st.error(f"❌ Error generating plan: {str(e)}")
            
            # Provide helpful error messages
            if "quota" in str(e).lower():
                st.warning("⚠️ API quota exceeded. Please wait a moment and try again, or check your API key limits.")
            elif "api key" in str(e).lower():
                st.warning("⚠️ API key issue. Please verify your API key is correct and active.")
            elif "blocked" in str(e).lower():
                st.warning("⚠️ Content was blocked by safety filters. Try rephrasing your request.")
            else:
                st.info("💡 Try these solutions:\n- Check your API key\n- Simplify your request\n- Wait a moment and try again\n- Ensure you have internet connection")
    
    # Chat History Section
    if st.session_state.chat_history:
        st.markdown("---")
        with st.expander("📜 View Previous Plans"):
            for i, entry in enumerate(reversed(st.session_state.chat_history[-5:])):
                st.markdown(f"**{entry['timestamp']}** - {entry['feature']}")
                st.text(entry['response'][:200] + "...")
                st.markdown("---")

else:
    # Instructions when API key is not configured
    st.info("👈 Please enter your Gemini API Key in the sidebar to get started.")
    
    st.markdown("### 🚀 Getting Started")
    st.markdown("""
    1. **Get your API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get your free Gemini API key
    2. **Enter the API Key**: Paste it in the sidebar
    3. **Fill your profile**: Complete your sport and fitness details
    4. **Choose a feature**: Select what you want help with
    5. **Generate your plan**: Click the button and get personalized coaching!
    """)
    
    st.markdown("### ✨ Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🏋️ Training Plans**
        - Full-body workouts
        - Recovery schedules
        - Strength programs
        - Speed & agility training
        """)
    
    with col2:
        st.markdown("""
        **🎯 Tactical Coaching**
        - Position-specific tips
        - Decision-making drills
        - Match preparation
        - Mental focus techniques
        """)
    
    with col3:
        st.markdown("""
        **🍽️ Nutrition & Recovery**
        - Weekly meal plans
        - Hydration strategies
        - Post-injury mobility
        - Tournament prep
        """)
    
    st.info("📊 **NEW**: Every plan includes organized training tables and schedules automatically!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>CoachBot AI</strong> - Empowering Young Athletes with AI-Powered Coaching</p>
    <p style='font-size: 0.9rem;'>⚠️ Disclaimer: This AI provides general guidance. Always consult with qualified coaches, 
    trainers, and medical professionals before starting any new training program.</p>
</div>
""", unsafe_allow_html=True)

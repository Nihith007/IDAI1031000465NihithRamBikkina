"""
Smart Fitness CoachBot - AI-Powered Personal Training Assistant
Powered by Google Gemini 2.0 Flash
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

with tab1:
# Sidebar for API Key and User Profile
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key from Streamlit Secrets or Input
        api_key = None
        
        # Try to get API key from Streamlit secrets first
        try:
            if 'GEMINI_API_KEY' in st.secrets:
                api_key = st.secrets['GEMINI_API_KEY']
                st.success("✅ API Key loaded from secrets!")
                genai.configure(api_key=api_key)
                st.session_state.api_key_configured = True
            else:
                # Fallback to manual input
                api_key = st.text_input("Enter Gemini API Key", type="password", 
                                       help="Get your API key from Google AI Studio or configure in Streamlit secrets")
                if api_key:
                    genai.configure(api_key=api_key)
                    st.session_state.api_key_configured = True
                    st.success("✅ API Key Configured!")
        except Exception as e:
            # If secrets not available, use text input
            api_key = st.text_input("Enter Gemini API Key", type="password", 
                                   help="Get your API key from Google AI Studio")
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    st.session_state.api_key_configured = True
                    st.success("✅ API Key Configured!")
                except Exception as e:
                    st.error(f"❌ Invalid API Key: {str(e)}")
                    st.session_state.api_key_configured = False
        
        st.markdown("---")
        
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
                "1. Full-Body Workout Plan for [Position] in [Sport]",
                "2. Safe Recovery Training Schedule for Athlete with [Injury]",
                "3. Tactical Coaching Tips to Improve [Skill] in [Sport]",
                "4. Week-Long Nutrition Guide for Young Athlete",
                "5. Personalized Warm-up & Cooldown Routine",
                "6. Mental Focus Routines for Tournaments",
                "7. Hydration & Electrolyte Strategy",
                "8. Pre-Match Visualization Techniques",
                "9. Positional Decision-Making Drills",
                "10. Mobility Workouts for Post-Injury Recovery"
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
            
            # Prompt templates for each feature (10 REQUIRED PROMPTS)
            prompts = {
                "1. Full-Body Workout Plan for [Position] in [Sport]": f"""
                As an experienced sports coach, create a comprehensive full-body workout plan for a {position} in {sport}.
                
                {user_context}
                
                Please provide:
                1. Detailed workout routine with exercises, sets, and reps
                2. Sport-specific exercises for their position
                3. Safety considerations based on injury history
                4. Progressive overload strategy
                5. Rest and recovery recommendations
                6. Weekly schedule with training days
                
                Format the response in a clear, structured manner with tables where appropriate.
                """,
                
                "2. Safe Recovery Training Schedule for Athlete with [Injury]": f"""
                As a sports physiotherapist and coach, create a safe recovery training schedule for an athlete with the following injury history: {injury_history if injury_history else 'General recovery needs'}.
                
                {user_context}
                
                Focus on:
                1. Low-impact exercises suitable for injury recovery
                2. Gradual progression back to full training (week-by-week plan)
                3. Specific exercises to AVOID based on injury history
                4. Flexibility and mobility work
                5. Timeline for recovery phases (Week 1, 2, 3, 4, etc.)
                6. Warning signs to watch for and when to rest
                7. Return-to-sport criteria
                
                Prioritize safety and long-term health over quick returns. Provide a structured recovery timeline.
                """,
                
                "3. Tactical Coaching Tips to Improve [Skill] in [Sport]": f"""
                As a tactical coach specializing in {sport}, provide advanced coaching tips for a {position} to improve their tactical skills and game awareness.
                
                {user_context}
                
                Include:
                1. Position-specific tactical awareness and responsibilities
                2. Game-reading skills to develop
                3. Decision-making scenarios and solutions
                4. Communication strategies with teammates
                5. Common tactical mistakes to avoid in this position
                6. Training drills to improve tactical understanding
                7. Professional examples and best practices
                
                Use specific examples from {sport} where relevant. Provide actionable tips.
                """,
                
                "4. Week-Long Nutrition Guide for Young Athlete": f"""
                As a sports nutritionist, create a comprehensive week-long nutrition guide for a {user_age}-year-old athlete.
                
                {user_context}
                
                Provide:
                1. Daily meal plans for 7 days (Breakfast, Lunch, Dinner, Snacks)
                2. Pre-training and post-training nutrition strategies
                3. Macro breakdown (Proteins, Carbs, Fats) in a table format
                4. Specific foods to support {sport} performance
                5. Timing of meals around training sessions
                6. Hydration recommendations throughout the day
                7. Age-appropriate supplement suggestions (if any)
                8. Sample grocery list
                
                Consider their dietary restrictions ({diet_type}, allergies: {allergies if allergies else 'none'}) and calorie goals ({calorie_goal}).
                Present meal plans in an organized table format for easy reference.
                """,
                
                "5. Personalized Warm-up & Cooldown Routine": f"""
                Create a personalized warm-up and cooldown routine specifically for a {position} in {sport}.
                
                {user_context}
                
                Include:
                1. Dynamic warm-up routine (10-15 minutes) - list specific exercises
                2. Sport-specific activation drills for {sport}
                3. Position-specific movement preparation for {position}
                4. Modifications based on injury history: {injury_history if injury_history else 'none'}
                5. Cooldown routine with static stretching (10-15 minutes)
                6. Foam rolling sequence and mobility work
                7. Breathing and recovery techniques
                
                Make it practical and easy to follow before every training session. Provide sets and duration for each exercise.
                """,
                
                "6. Mental Focus Routines for Tournaments": f"""
                As a sports psychologist, create a comprehensive mental preparation program for a {user_age}-year-old {position} preparing for tournaments in {sport}.
                
                {user_context}
                
                Cover:
                1. Pre-tournament mental preparation (weeks before)
                2. Week-of-tournament daily routines
                3. Day-before and morning-of mental checklist
                4. Visualization techniques specific to {sport} and {position}
                5. Pressure management and performance anxiety strategies
                6. Focus and concentration drills
                7. Dealing with nervousness and pre-game jitters
                8. Post-performance reflection techniques
                9. Building confidence and positive self-talk
                
                Make it age-appropriate for a {user_age}-year-old and practical to implement.
                """,
                
                "7. Hydration & Electrolyte Strategy": f"""
                Design a comprehensive hydration and electrolyte strategy for a young {sport} athlete.
                
                {user_context}
                
                Provide:
                1. Daily water intake recommendations (in liters/ml)
                2. Pre-training hydration protocol (timing and amounts)
                3. During-training hydration strategy
                4. Post-training rehydration plan
                5. Electrolyte balance strategies and when to use sports drinks
                6. Signs of dehydration to watch for
                7. Sport-specific hydration needs for {sport}
                8. Hydration strategies for different weather conditions
                9. Recommended drinks and timing throughout the day
                10. Weekly hydration schedule table
                
                Consider their age ({user_age}) and training intensity ({training_intensity}).
                Present in an organized format with clear guidelines.
                """,
                
                "8. Pre-Match Visualization Techniques": f"""
                Teach effective pre-match visualization techniques for a {position} in {sport}.
                
                {user_context}
                
                Include:
                1. Step-by-step visualization process (how to do it)
                2. What specifically to visualize as a {position} in {sport}
                3. Successful plays and scenarios to imagine
                4. Positioning and movement patterns to rehearse mentally
                5. When to practice visualization (timeline before match)
                6. Combining visualization with breathing techniques
                7. Confidence-building mental imagery
                8. Dealing with negative thoughts and doubts
                9. Creating a consistent pre-match mental routine
                10. Sample visualization script for {sport}
                
                Make it practical for a {user_age}-year-old athlete to implement independently.
                """,
                
                "9. Positional Decision-Making Drills": f"""
                Create position-specific decision-making drills for a {position} in {sport}.
                
                {user_context}
                
                Provide:
                1. Situational awareness drills specific to {position}
                2. Quick decision-making exercises under pressure
                3. Game-like scenarios to practice (at least 5 scenarios)
                4. Reading the game/opposition drills
                5. Positioning and movement decision drills
                6. Progressive difficulty levels (beginner to advanced)
                7. Solo practice drills (can do alone)
                8. Partner/team drills (with teammates)
                9. Video analysis recommendations
                10. Performance metrics to track improvement
                
                Focus on improving game intelligence and decision-making speed for {position}.
                Provide clear instructions for each drill.
                """,
                
                "10. Mobility Workouts for Post-Injury Recovery": f"""
                Create a comprehensive mobility and flexibility program for post-injury recovery.
                
                {user_context}
                
                Include:
                1. Gentle mobility exercises for affected areas: {injury_history if injury_history else 'general recovery'}
                2. Full-body mobility routine (not just injured area)
                3. Dynamic stretching sequences
                4. Yoga-inspired movements for athletes
                5. Frequency recommendations (daily schedule)
                6. Duration for each session
                7. Progression markers (when to advance)
                8. Exercises to avoid during recovery
                9. Pain management and when to stop
                10. Timeline: Week 1-2, Week 3-4, Week 5-6, etc.
                11. Return-to-sport mobility standards
                
                Emphasize safety and gradual progression. Provide detailed instructions with sets/reps/duration.
                Make it specific to {sport} demands.
                """
            }
            
            selected_prompt = prompts.get(feature, prompts["1. Full-Body Workout Plan for [Position] in [Sport]"])
            
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

with tab2:
    st.subheader("🧠 Custom Coach Consultation")
    user_query = st.text_area("Ask a specific coaching question:", 
                             placeholder="e.g., Suggest 3 drills for explosive speed.")
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        intensity_val = st.slider("Advice Intensity", 1, 100, 40)
        ai_temp = intensity_val / 100.0

    if st.button("Ask AI Coach", type="primary"):
        if user_query:
            custom_model = genai.GenerativeModel("gemini-2.5-flash", 
                                               generation_config={"temperature": ai_temp})
            
            custom_prompt = (
                f"User Question: {user_query}. Advice Intensity: {intensity_val}/100. "
                "STRICT RULES: Output ONLY a short, technical Markdown table. NO HTML tags like <br>. "
                "Keep descriptions extremely concise."
            )
            
            with st.spinner("Consulting AI Coach..."):
                answer = get_ai_response(custom_model, custom_prompt)
                st.info("📋 Quick Coaching Chart:")
                st.markdown(answer)
    
# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>CoachBot AI</strong> - Empowering Young Athletes with AI-Powered Coaching</p>
    <p style='font-size: 0.9rem;'>⚠️ Disclaimer: This AI provides general guidance. Always consult with qualified coaches, 
    trainers, and medical professionals before starting any new training program.</p>
</div>
""", unsafe_allow_html=True)

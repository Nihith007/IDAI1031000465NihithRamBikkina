"""
Smart Fitness CoachBot - AI-Powered Personal Training Assistant
Powered by Google Gemini 2.0 Flash
"""

import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import re

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
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_weekly_training_schedule_chart(training_data):
    """Create a bar chart showing weekly training schedule"""
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    if training_data:
        intensities = training_data
    else:
        intensities = [8, 6, 9, 5, 7, 4, 2]
    
    fig = go.Figure()
    colors = ['#1E88E5', '#43A047', '#FB8C00', '#E53935', '#8E24AA', '#00ACC1', '#7CB342']
    
    fig.add_trace(go.Bar(
        x=days,
        y=intensities,
        marker_color=colors,
        text=intensities,
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Intensity: %{y}/10<extra></extra>'
    ))
    
    fig.update_layout(
        title='Weekly Training Intensity Schedule',
        xaxis_title='Day of Week',
        yaxis_title='Training Intensity (1-10)',
        yaxis_range=[0, 10],
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return fig

def create_training_distribution_pie(training_types):
    """Create a pie chart showing training type distribution"""
    
    if training_types:
        labels = list(training_types.keys())
        values = list(training_types.values())
    else:
        labels = ['Strength Training', 'Cardio/Endurance', 'Skill Work', 
                  'Flexibility/Mobility', 'Rest/Recovery']
        values = [25, 30, 25, 10, 10]
    
    colors = ['#1E88E5', '#43A047', '#FB8C00', '#E53935', '#8E24AA']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>%{value}%<br>%{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title='Training Type Distribution',
        template='plotly_white',
        height=400,
        showlegend=True
    )
    
    return fig

def create_nutrition_macro_pie(macros):
    """Create a pie chart for nutrition macros"""
    
    if macros:
        labels = list(macros.keys())
        values = list(macros.values())
    else:
        labels = ['Protein', 'Carbohydrates', 'Fats']
        values = [30, 45, 25]
    
    colors = ['#E53935', '#FB8C00', '#43A047']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
        marker_colors=colors,
        textinfo='label+percent',
        textfont_size=14
    )])
    
    fig.update_layout(
        title='Daily Macro Distribution (%)',
        template='plotly_white',
        height=400
    )
    
    return fig

def create_progress_timeline_chart(weeks=8):
    """Create a line chart showing expected progress timeline"""
    
    weeks_list = list(range(1, weeks + 1))
    strength = [20, 30, 42, 55, 65, 75, 82, 90][:weeks]
    endurance = [25, 35, 45, 58, 68, 76, 84, 92][:weeks]
    skill = [30, 38, 48, 58, 68, 76, 83, 89][:weeks]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=weeks_list, y=strength,
        mode='lines+markers',
        name='Strength',
        line=dict(color='#1E88E5', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=weeks_list, y=endurance,
        mode='lines+markers',
        name='Endurance',
        line=dict(color='#43A047', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=weeks_list, y=skill,
        mode='lines+markers',
        name='Skill Level',
        line=dict(color='#FB8C00', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title=f'{weeks}-Week Progress Timeline',
        xaxis_title='Week',
        yaxis_title='Progress Level (%)',
        yaxis_range=[0, 100],
        template='plotly_white',
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_workout_volume_chart():
    """Create a stacked bar chart showing workout volume by muscle group"""
    
    muscle_groups = ['Legs', 'Back', 'Chest', 'Shoulders', 'Arms', 'Core']
    strength_sets = [12, 10, 8, 6, 8, 10]
    endurance_sets = [8, 6, 5, 4, 5, 8]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Strength Sets',
        x=muscle_groups,
        y=strength_sets,
        marker_color='#1E88E5'
    ))
    
    fig.add_trace(go.Bar(
        name='Endurance Sets',
        x=muscle_groups,
        y=endurance_sets,
        marker_color='#43A047'
    ))
    
    fig.update_layout(
        title='Weekly Training Volume by Muscle Group',
        xaxis_title='Muscle Group',
        yaxis_title='Number of Sets',
        barmode='stack',
        template='plotly_white',
        height=400
    )
    
    return fig

def display_visualization_dashboard(feature_type, training_frequency, training_duration):
    """Display appropriate visualizations based on feature type"""
    
    st.markdown("---")
    st.markdown("## 📊 Training Visualizations & Analytics")
    st.markdown("*Automatically generated based on your training plan*")
    
    # ALWAYS show these two core charts for ALL features
    st.markdown("### 📅 Your Weekly Training Schedule")
    col1, col2 = st.columns(2)
    
    with col1:
        # Training Schedule Bar Chart - ALWAYS SHOWN
        st.plotly_chart(create_weekly_training_schedule_chart(None), use_container_width=True)
    
    with col2:
        # Training Distribution Pie Chart - ALWAYS SHOWN
        if "Nutrition" in feature_type:
            macros = {'Protein': 30, 'Carbohydrates': 45, 'Fats': 25}
            st.plotly_chart(create_nutrition_macro_pie(macros), use_container_width=True)
        else:
            training_types = {
                'Strength Training': 30,
                'Cardio/Endurance': 25,
                'Skill Work': 25,
                'Flexibility': 10,
                'Rest/Recovery': 10
            }
            st.plotly_chart(create_training_distribution_pie(training_types), use_container_width=True)
    
    # Additional feature-specific charts
    st.markdown("### 📈 Additional Analytics")
    
    if "Workout" in feature_type or "Training" in feature_type or "Strength" in feature_type:
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.plotly_chart(create_progress_timeline_chart(8), use_container_width=True)
        
        with col4:
            st.plotly_chart(create_workout_volume_chart(), use_container_width=True)
    
    elif "Nutrition" in feature_type:
        
        col3, col4 = st.columns(2)
        
        with col3:
            meal_dist = {
                'Breakfast': 25,
                'Lunch': 30,
                'Dinner': 30,
                'Snacks': 15
            }
            st.plotly_chart(create_training_distribution_pie(meal_dist), use_container_width=True)
        
        with col4:
            st.plotly_chart(create_progress_timeline_chart(7), use_container_width=True)
    
    elif "Recovery" in feature_type or "Mobility" in feature_type:
        
        col3, col4 = st.columns(2)
        
        with col3:
            recovery_types = {
                'Stretching': 30,
                'Foam Rolling': 20,
                'Low Impact Cardio': 25,
                'Rest': 25
            }
            st.plotly_chart(create_training_distribution_pie(recovery_types), use_container_width=True)
        
        with col4:
            st.plotly_chart(create_progress_timeline_chart(8), use_container_width=True)
    
    elif "Endurance" in feature_type or "Speed" in feature_type:
        
        col3, col4 = st.columns(2)
        
        with col3:
            training_types = {
                'Interval Training': 35,
                'Long Distance': 30,
                'Speed Work': 20,
                'Recovery Runs': 15
            }
            st.plotly_chart(create_training_distribution_pie(training_types), use_container_width=True)
        
        with col4:
            st.plotly_chart(create_progress_timeline_chart(12), use_container_width=True)
    
    else:
        col3, col4 = st.columns(2)
        
        with col3:
            default_types = {
                'Physical Training': 40,
                'Skill Development': 30,
                'Mental Training': 15,
                'Recovery': 15
            }
            st.plotly_chart(create_training_distribution_pie(default_types), use_container_width=True)
        
        with col4:
            st.plotly_chart(create_progress_timeline_chart(8), use_container_width=True)

# Header
st.markdown('<h1 class="main-header">🏋️ CoachBot AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your Personal AI Fitness & Sports Coach - Powered by Gemini 2.0 Flash</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #1E88E5; font-weight: 500;">✨ Now with Interactive Training Graphs & Analytics ✨</p>', unsafe_allow_html=True)

# Sidebar for API Key and User Profile
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key Input
    api_key = st.text_input("Enter Gemini API Key", type="password", help="Get your API key from Google AI Studio")
    
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
        st.markdown("**📊 Visualization Settings**")
        show_charts = st.checkbox("Show Training Visualizations", value=True, 
                                   help="Display charts and graphs with your plan")
        
        if show_charts:
            chart_style = st.selectbox(
                "Chart Style",
                ["Default", "Dark Mode", "Minimal", "Colorful"],
                help="Choose visualization theme"
            )
    
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
                    model_name="gemini-2.0-flash-exp",
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
                
                # Display visualizations if enabled
                if 'show_charts' not in locals() or show_charts:
                    display_visualization_dashboard(feature, training_frequency, training_duration)
                
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
    
    st.info("📊 **NEW**: Every plan includes interactive training schedule graphs and pie charts automatically!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>CoachBot AI</strong> - Empowering Young Athletes with AI-Powered Coaching</p>
    <p style='font-size: 0.9rem;'>⚠️ Disclaimer: This AI provides general guidance. Always consult with qualified coaches, 
    trainers, and medical professionals before starting any new training program.</p>
</div>
""", unsafe_allow_html=True)

"""
CoachBot AI - Smart Fitness Assistance Web Application
Powered by Google Gemini 2.5 Flash
"""

import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CoachBot AI - Your Personal Fitness Coach",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CSS  — same as previous app
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "api_key_configured" not in st.session_state:
    st.session_state.api_key_configured = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ─────────────────────────────────────────────
# AI HELPER
# ─────────────────────────────────────────────
def get_ai_response(model, prompt):
    """Call the model and clean up stray HTML."""
    try:
        response = model.generate_content(prompt)
        if not response.text:
            return "⚠️ Response was blocked or empty. Please try again."
        return (response.text
                .replace("<br>", "\n")
                .replace("</br>", "")
                .replace("<div>", "")
                .replace("</div>", ""))
    except Exception as e:
        err = str(e)
        if "quota" in err.lower():
            return "⚠️ API quota exceeded. Please wait and try again."
        if "api key" in err.lower():
            return "⚠️ Invalid API key. Please check your configuration."
        return f"⚠️ Error: {err}"

# ─────────────────────────────────────────────
# REFERENCE TABLE BUILDERS
# ─────────────────────────────────────────────
def create_weekly_training_table(intensity="Moderate"):
    scores = {
        "Low":       [4, 3, 5, 2, 4, 3, 1],
        "Moderate":  [6, 5, 7, 3, 6, 4, 2],
        "High":      [8, 6, 9, 4, 7, 5, 2],
        "Very High": [9, 7, 10, 5, 8, 6, 2],
    }.get(intensity, [6, 5, 7, 3, 6, 4, 2])
    return pd.DataFrame({
        "Day":               ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
        "Focus":             ["Strength Training","Cardio/Endurance","Sport-Specific Skills",
                              "Recovery/Mobility","Strength + Conditioning","Light Cardio","Rest/Active Recovery"],
        "Duration":          ["60 min","45 min","75 min","30 min","60 min","30 min","20 min"],
        "Intensity (1-10)":  scores,
    })

def create_training_distribution_table():
    return pd.DataFrame({
        "Training Type":   ["Strength Training","Cardio/Endurance","Skill Work",
                            "Flexibility/Mobility","Rest/Recovery"],
        "Percentage (%)":  [30, 25, 25, 10, 10],
        "Hours per Week":  [3.0, 2.5, 2.5, 1.0, 1.0],
    })

def create_nutrition_table(calorie_goal="Maintenance"):
    g, c = {
        "Maintenance":            ("150g","280g","70g","2350 kcal"),
        "Deficit (Weight Loss)":  ("140g","240g","60g","2000 kcal"),
        "Surplus (Muscle Gain)":  ("180g","340g","85g","2800 kcal"),
    }.get(calorie_goal, ("150g","280g","70g","2350 kcal")), None
    vals = g
    return pd.DataFrame({
        "Nutrient":       ["Protein","Carbohydrates","Fats","Total Calories"],
        "Percentage":     ["30%","45%","25%","100%"],
        "Grams per Day":  [vals[0], vals[1], vals[2], "—"],
        "Calories":       ["varies","varies","varies", vals[3]],
    })

def create_weekly_meal_plan_table():
    return pd.DataFrame({
        "Day":       ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
        "Breakfast": ["Oatmeal + Eggs","Greek Yogurt + Fruits","Whole Grain Toast + Avocado",
                      "Protein Smoothie","Scrambled Eggs + Veggies","Pancakes + Berries","Omelet + Toast"],
        "Lunch":     ["Chicken + Rice + Veggies","Fish + Quinoa Salad","Turkey Wrap + Soup",
                      "Pasta + Lean Meat","Grilled Chicken Salad","Rice Bowl + Protein","Sandwich + Fruit"],
        "Dinner":    ["Salmon + Sweet Potato","Lean Beef + Brown Rice","Chicken Stir-fry",
                      "Fish + Vegetables","Turkey + Quinoa","Grilled Chicken + Pasta","Lean Meat + Rice"],
        "Snacks":    ["Protein Bar + Nuts","Fruit + Cheese","Hummus + Veggies",
                      "Greek Yogurt","Trail Mix","Protein Shake","Fruit + Nut Butter"],
    })

def create_exercise_table():
    return pd.DataFrame({
        "Exercise":   ["Squats","Bench Press","Deadlifts","Pull-ups",
                       "Shoulder Press","Lunges","Rows","Core Work"],
        "Sets":       [4, 4, 3, 3, 3, 3, 4, 3],
        "Reps":       ["8-10","8-10","6-8","8-12","10-12","10 each leg","10-12","15-20"],
        "Rest (sec)": [90, 90, 120, 90, 60, 60, 75, 45],
        "Notes":      ["Focus on form","Control the weight","Keep back straight",
                       "Use assistance if needed","Full range of motion","Maintain balance",
                       "Squeeze at top","Engage core throughout"],
    })

def create_progress_tracking_table(weeks=8):
    w  = list(range(1, weeks + 1))
    s  = [20,30,42,55,65,75,82,90,93,95,97,99][:weeks]
    e  = [25,35,45,58,68,76,84,92,94,96,98,99][:weeks]
    k  = [30,38,48,58,68,76,83,89,91,93,95,97][:weeks]
    bw = [70,70.5,71,71.2,71.5,71.8,72,72.2,72.3,72.4,72.5,72.6][:weeks]
    notes = ["Baseline","Good progress","Increasing intensity","Maintaining form",
             "Peak week","Recovery focus","Final push","Assessment week",
             "Advanced","Near peak","Optimising","Elite"][:weeks]
    return pd.DataFrame({
        "Week": w, "Strength (%)": s, "Endurance (%)": e,
        "Skill Level (%)": k, "Body Weight (kg)": bw, "Notes": notes,
    })

def create_injury_recovery_table():
    return pd.DataFrame({
        "Phase":      ["Week 1-2","Week 3-4","Week 5-6","Week 7-8","Week 9+"],
        "Focus":      ["Pain Management","Gentle Movement","Strength Building",
                       "Sport-Specific Work","Full Training"],
        "Intensity":  ["Very Low (2-3/10)","Low (3-4/10)","Moderate (5-6/10)",
                       "High (7-8/10)","Full (9-10/10)"],
        "Activities": ["Ice, Rest, Gentle Stretching","Pool Work, Light Mobility",
                       "Resistance Bands, Bodyweight","Light Sport Drills","Full Practice"],
        "Red Flags":  ["Sharp pain, Swelling","Persistent pain","Limited ROM",
                       "Pain during sport moves","Recurring issues"],
    })

def display_tabular_dashboard(feature_type, training_intensity, calorie_goal):
    """Show reference tables below the AI output — same logic as before."""
    st.markdown("---")
    st.markdown("## 📊 Training Schedule & Breakdown (Tables)")
    st.markdown("*Organised reference data to support your plan*")

    st.markdown("### 📅 Weekly Training Schedule")
    st.dataframe(create_weekly_training_table(training_intensity),
                 use_container_width=True, hide_index=True)

    if any(k in feature_type for k in ["Workout","Training Plan","Strength","Decision",
                                        "Drill","Warm","Tactical","Mental","Visualization"]):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 💪 Exercise Routine")
            st.dataframe(create_exercise_table(), use_container_width=True, hide_index=True)
        with c2:
            st.markdown("### 📈 Training Distribution")
            st.dataframe(create_training_distribution_table(), use_container_width=True, hide_index=True)
        st.markdown("### 📊 8-Week Progress Tracking")
        st.dataframe(create_progress_tracking_table(8), use_container_width=True, hide_index=True)

    elif "Nutrition" in feature_type:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🍽️ Macro Breakdown")
            st.dataframe(create_nutrition_table(calorie_goal), use_container_width=True, hide_index=True)
        with c2:
            st.markdown("### 📋 Meal Calorie Distribution")
            st.dataframe(pd.DataFrame({
                "Meal":       ["Breakfast","Lunch","Dinner","Snacks"],
                "Calorie %":  [25, 30, 30, 15],
            }), use_container_width=True, hide_index=True)
        st.markdown("### 🗓️ Weekly Meal Plan")
        st.dataframe(create_weekly_meal_plan_table(), use_container_width=True, hide_index=True)

    elif any(k in feature_type for k in ["Recovery","Mobility","Hydration"]):
        st.markdown("### 🏥 Recovery Timeline")
        st.dataframe(create_injury_recovery_table(), use_container_width=True, hide_index=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🧘 Recovery Activities")
            st.dataframe(pd.DataFrame({
                "Activity":  ["Stretching","Foam Rolling","Low Impact Cardio","Rest"],
                "Time %":    [30, 20, 25, 25],
            }), use_container_width=True, hide_index=True)
        with c2:
            st.markdown("### 📊 Progress Tracking")
            pt = create_progress_tracking_table(8)
            st.dataframe(pt[["Week","Strength (%)","Endurance (%)"]],
                         use_container_width=True, hide_index=True)
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 📋 Training Distribution")
            st.dataframe(pd.DataFrame({
                "Category":      ["Physical Training","Skill Development","Mental Training","Recovery"],
                "Percentage %":  [40, 30, 15, 15],
            }), use_container_width=True, hide_index=True)
        with c2:
            st.markdown("### 📊 Progress Tracking")
            pt = create_progress_tracking_table(8)
            st.dataframe(pt[["Week","Strength (%)","Skill Level (%)"]],
                         use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# SPORT / POSITION DATA
# ─────────────────────────────────────────────
position_options = {
    "Football/Soccer":         ["Goalkeeper","Defender","Midfielder","Forward/Striker","Winger"],
    "Cricket":                 ["Batsman","Bowler (Fast)","Bowler (Spin)","All-rounder","Wicket-keeper"],
    "Basketball":              ["Point Guard","Shooting Guard","Small Forward","Power Forward","Center"],
    "Athletics/Track & Field": ["Sprinter","Middle Distance","Long Distance","Jumper","Thrower"],
    "Tennis":                  ["Singles Player","Doubles Player","Baseline Player","Serve-and-Volley"],
    "Swimming":                ["Freestyle","Backstroke","Breaststroke","Butterfly","Individual Medley"],
    "Volleyball":              ["Setter","Outside Hitter","Middle Blocker","Libero","Opposite Hitter"],
    "Badminton":               ["Singles Player","Doubles Player","Mixed Doubles"],
    "Hockey":                  ["Forward","Midfielder","Defender","Goalkeeper"],
    "Kabaddi":                 ["Raider","Defender","All-Rounder"],
    "Rugby":                   ["Forward","Back"],
    "Other":                   ["General Athlete"],
}

# ─────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────
st.markdown('<h1 class="main-header">🏋️ CoachBot AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your Personal AI Fitness & Sports Coach - Powered by Gemini 2.5 Flash</p>',
            unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#1E88E5;font-weight:500;">'
            '✨ Personalised Plans with Explanations + Organised Training Tables ✨</p>',
            unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")

    api_key = None
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            st.success("✅ API Key loaded from secrets!")
            genai.configure(api_key=api_key)
            st.session_state.api_key_configured = True
        else:
            api_key = st.text_input("Enter Gemini API Key", type="password",
                                    help="Get your key from Google AI Studio")
            if api_key:
                genai.configure(api_key=api_key)
                st.session_state.api_key_configured = True
                st.success("✅ API Key Configured!")
    except Exception:
        api_key = st.text_input("Enter Gemini API Key", type="password",
                                help="Get your key from Google AI Studio")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                st.session_state.api_key_configured = True
                st.success("✅ API Key Configured!")
            except Exception as e:
                st.error(f"❌ Invalid API Key: {e}")
                st.session_state.api_key_configured = False

    st.markdown("---")
    st.header("👤 Your Profile")
    user_name   = st.text_input("Name", placeholder="e.g. Sarah")
    user_age    = st.number_input("Age", min_value=10, max_value=100, value=15)
    user_gender = st.selectbox("Gender", ["Male","Female","Other","Prefer not to say"])

    st.markdown("---")
    st.header("⚽ Sport Details")
    sport    = st.selectbox("Select Your Sport", list(position_options.keys()))
    position = st.selectbox("Player Position", position_options[sport])

    st.markdown("---")
    st.header("🎯 Fitness Details")
    fitness_level  = st.select_slider("Current Fitness Level",
                                      options=["Beginner","Intermediate","Advanced","Elite"])
    injury_history = st.text_area("Injury History / Risk Zones",
                                  placeholder="e.g. Previous ankle sprain, knee sensitivity")

    st.markdown("---")
    st.header("🍽️ Nutrition Preferences")
    diet_type    = st.selectbox("Diet Type", ["Vegetarian","Non-Vegetarian","Vegan","Pescatarian"])
    allergies    = st.text_input("Allergies / Food Restrictions", placeholder="e.g. Nuts, dairy")
    calorie_goal = st.select_slider("Daily Calorie Goal",
                                    options=["Maintenance","Deficit (Weight Loss)","Surplus (Muscle Gain)"])

# ─────────────────────────────────────────────
# MAIN AREA
# ─────────────────────────────────────────────
if st.session_state.api_key_configured:

    tab1, tab2 = st.tabs(["📊 Smart Assistant", "🧠 Custom Coach"])

    # ══════════════════════════════════════════
    # TAB 1 — SMART ASSISTANT
    # ══════════════════════════════════════════
    with tab1:

        st.header("🎯 What would you like CoachBot to help you with?")

        feature = st.selectbox("Select a Feature", [
            "1. Full-Body Workout Plan for [Position] in [Sport]",
            "2. Safe Recovery Training Schedule for Athlete with [Injury]",
            "3. Tactical Coaching Tips to Improve [Skill] in [Sport]",
            "4. Week-Long Nutrition Guide for Young Athlete",
            "5. Personalized Warm-up & Cooldown Routine",
            "6. Mental Focus Routines for Tournaments",
            "7. Hydration & Electrolyte Strategy",
            "8. Pre-Match Visualization Techniques",
            "9. Positional Decision-Making Drills",
            "10. Mobility Workouts for Post-Injury Recovery",
        ])

        col1, col2 = st.columns(2)
        with col1:
            training_intensity = st.select_slider("Training Intensity",
                                                   options=["Low","Moderate","High","Very High"])
            training_duration  = st.selectbox("Training Duration per Session",
                                              ["30 minutes","45 minutes","60 minutes",
                                               "90 minutes","120 minutes"])
        with col2:
            training_frequency = st.selectbox("Training Frequency",
                                              ["2-3 times/week","4-5 times/week",
                                               "6 times/week","Daily"])
            specific_goal      = st.text_input("Specific Goal",
                                               placeholder="e.g. Improve stamina, tournament prep")

        with st.expander("🔧 Advanced Settings (Optional)"):
            temperature = st.slider("AI Creativity Level", 0.0, 1.0, 0.5, 0.1,
                                    help="Lower = conservative  |  Higher = creative")
            st.markdown("---")
            st.markdown("**📊 Display Settings**")
            show_tables = st.checkbox("Show Training Tables & Data", value=True,
                                      help="Display reference tables below your plan")

        if st.button("🚀 Generate Personalized Plan", type="primary"):

            # Full user context injected into every prompt
            user_context = f"""
Athlete Profile:
- Name: {user_name if user_name else 'Athlete'}
- Age: {user_age} years old
- Gender: {user_gender}
- Sport: {sport}
- Position: {position}
- Current Fitness Level: {fitness_level}
- Injury History / Risk Zones: {injury_history if injury_history else 'None'}
- Diet Type: {diet_type}
- Food Allergies / Restrictions: {allergies if allergies else 'None'}
- Daily Calorie Goal: {calorie_goal}
- Training Intensity: {training_intensity}
- Training Duration per Session: {training_duration}
- Training Frequency: {training_frequency}
- Specific Goal: {specific_goal if specific_goal else 'General improvement'}
"""

            # ── 10 PROMPTS — text explanations + embedded tables ──
            prompts = {

"1. Full-Body Workout Plan for [Position] in [Sport]": f"""
You are an experienced sports coach. Create a full-body workout plan personalised for this athlete.

{user_context}

Write your response in this exact format:
1. Start with 2-3 paragraphs of text explaining the overall approach, why it suits this athlete's sport and position, any modifications for their injury history, and what they should focus on at their fitness level.
2. Then include a Markdown table: Weekly Schedule (Day | Focus | Exercises | Sets x Reps | Duration | Intensity).
3. Then 1-2 paragraphs explaining progressive overload and how intensity should increase over the training period.
4. Then a Markdown table: Exercise Details (Exercise | Sets | Reps | Rest (sec) | Key Technique Tip | Injury Modification).
5. End with a short paragraph on recovery and rest advice specific to their age and goal.

Use their name if provided. Reference their sport and position throughout. Be specific to their fitness level.
""",

"2. Safe Recovery Training Schedule for Athlete with [Injury]": f"""
You are a sports physiotherapist and coach. Create a safe injury recovery programme for this athlete.

{user_context}

Write your response in this exact format:
1. Start with 2-3 paragraphs explaining the recovery approach, why these phases suit their specific injury history, and key safety principles to follow.
2. Then include a Markdown table: Recovery Timeline (Phase | Weeks | Focus | Exercises | Load Level | Duration/Day).
3. Then 1-2 paragraphs explaining what warning signs to watch for and when to seek professional help.
4. Then a Markdown table: Exercises to AVOID (Exercise | Reason | Safe Alternative Instead).
5. End with a paragraph on return-to-sport criteria and mental readiness.

If injury history is 'None', create a general recovery/prevention plan. Be conservative and safety-first throughout.
""",

"3. Tactical Coaching Tips to Improve [Skill] in [Sport]": f"""
You are a tactical coach specialising in {sport}. Give advanced coaching advice for this athlete.

{user_context}

Write your response in this exact format:
1. Start with 2-3 paragraphs describing the key tactical responsibilities of a {position} in {sport}, what skills they must develop, and how their fitness level and goal affect tactical training.
2. Then include a Markdown table: Key Tactical Scenarios (Situation | What To Read | Best Response | Common Mistake).
3. Then 1-2 paragraphs on developing game intelligence and communication with teammates.
4. Then a Markdown table: Training Drills (Drill Name | Duration | Players Needed | Instructions | KPI to Measure).
5. End with a short paragraph on professional examples and how to study the game.

Reference their specific position, sport, and goal throughout.
""",

"4. Week-Long Nutrition Guide for Young Athlete": f"""
You are a sports nutritionist. Create a personalised week-long nutrition guide for this athlete.

{user_context}

Write your response in this exact format:
1. Start with 2-3 paragraphs explaining the nutritional approach for their sport, why the macro split suits their goal ({calorie_goal}), and how to handle their dietary restrictions ({diet_type}, allergies: {allergies if allergies else 'none'}).
2. Then include a Markdown table: Daily Macros (Nutrient | Grams/Day | % of Total | Calories | Best Food Sources).
3. Then 1-2 paragraphs on meal timing around training sessions and its importance for performance.
4. Then a Markdown table: 7-Day Meal Plan (Day | Breakfast | Lunch | Dinner | Snacks | Approx kcal).
5. End with a paragraph on hydration targets and practical grocery tips.

Adapt all meals to {diet_type} and exclude {allergies if allergies else 'no allergens'}. Reference their age and sport throughout.
""",

"5. Personalized Warm-up & Cooldown Routine": f"""
You are a professional strength and conditioning coach. Create a warm-up and cooldown routine for this athlete.

{user_context}

Write your response in this exact format:
1. Start with 2 paragraphs explaining why a proper warm-up matters for a {position} in {sport}, and how injury history ({injury_history if injury_history else 'none'}) affects the routine.
2. Then include a Markdown table: Dynamic Warm-up (Exercise | Duration | Sets | Purpose | Injury Modification).
3. Then 1 paragraph explaining the sport-specific activation phase and what it prepares the athlete for.
4. Then a Markdown table: Cooldown & Stretching (Exercise | Hold Duration | Target Muscle | Benefit | Notes).
5. End with a short paragraph on foam rolling sequence and breathing techniques for recovery.

Make the routine practical for {training_duration} sessions at {training_intensity} intensity.
""",

"6. Mental Focus Routines for Tournaments": f"""
You are a sports psychologist. Build a mental preparation programme for this athlete.

{user_context}

Write your response in this exact format:
1. Start with 2-3 paragraphs explaining the mental challenges for a {user_age}-year-old {position} in tournament {sport}, and the overall psychological approach to competition preparation.
2. Then include a Markdown table: Pre-Tournament Timeline (Days Before | Mental Activity | Duration | Goal | How To Do It).
3. Then 1-2 paragraphs on managing performance anxiety, dealing with nerves, and building confidence specifically for {sport}.
4. Then a Markdown table: Match-Day Mental Routine (Time | Activity | Duration | Purpose | Technique).
5. End with a paragraph on post-performance reflection and positive self-talk strategies.

Be age-appropriate for {user_age} years old and reference {sport} scenarios throughout.
""",

"7. Hydration & Electrolyte Strategy": f"""
You are a sports nutrition and hydration specialist. Build a hydration strategy for this athlete.

{user_context}

Write your response in this exact format:
1. Start with 2-3 paragraphs explaining why hydration is critical for {sport} at {training_intensity} intensity, how dehydration impacts performance, and the general daily targets for a {user_age}-year-old athlete.
2. Then include a Markdown table: Daily Hydration Schedule (Time of Day | Amount (ml) | Drink Type | Purpose | Notes).
3. Then 1-2 paragraphs on electrolyte balance, when to use sports drinks vs water, and hot/cold weather adjustments.
4. Then a Markdown table: Training Hydration Protocol (Phase | Timing | Amount | Electrolytes Needed | Warning Signs).
5. End with a short paragraph on recognising dehydration early and practical tips for staying consistent.

Reference their training frequency ({training_frequency}) and duration ({training_duration}) throughout.
""",

"8. Pre-Match Visualization Techniques": f"""
You are a sports psychologist specialising in mental performance. Teach visualisation techniques for this athlete.

{user_context}

Write your response in this exact format:
1. Start with 2-3 paragraphs explaining what visualisation is, why it works for athletes, and how a {position} in {sport} can specifically benefit from it before matches.
2. Then include a Markdown table: Visualisation Timeline (Time Before Match | Activity | Duration | What to Visualise | Expected Benefit).
3. Then 1-2 paragraphs on combining breathing techniques with mental imagery and how to handle negative thoughts that arise.
4. Then a Markdown table: Position-Specific Scenarios to Visualise (Scenario | What to See | What to Feel | Outcome to Imagine).
5. End with a sample 5-minute visualisation script written specifically for a {position} in {sport}.

Make it practical for a {user_age}-year-old. Reference their specific position throughout.
""",

"9. Positional Decision-Making Drills": f"""
You are a professional {sport} coach. Design decision-making drills for this athlete.

{user_context}

Write your response in this exact format:
1. Start with 2-3 paragraphs explaining the decision-making demands of a {position} in {sport}, the key cognitive skills to develop, and how training at {training_intensity} intensity helps build game intelligence.
2. Then include a Markdown table: Core Drills (Drill Name | Duration | Players Needed | Instructions | Progression | KPI).
3. Then 1-2 paragraphs on how to practice decision-making alone (solo drills) and the mental habits to build between sessions.
4. Then a Markdown table: Game Scenarios (Situation | Options Available | Best Decision | Why | Common Error).
5. End with a short paragraph on tracking improvement and integrating drills into team training sessions.

All drills must be specific to {position} in {sport}. Reference their fitness level and goal.
""",

"10. Mobility Workouts for Post-Injury Recovery": f"""
You are a sports physiotherapist and mobility specialist. Design a post-injury mobility programme for this athlete.

{user_context}

Write your response in this exact format:
1. Start with 2-3 paragraphs explaining the importance of mobility work for {sport}, how their injury history ({injury_history if injury_history else 'general recovery'}) shapes this programme, and the key principles of safe progression.
2. Then include a Markdown table: Phase-by-Phase Plan (Phase | Weeks | Focus | Key Exercises | Load | Daily Duration).
3. Then 1-2 paragraphs on exercises to strictly avoid during recovery, pain management strategies, and when to seek professional support.
4. Then a Markdown table: Daily Mobility Routine (Exercise | Sets | Duration/Reps | Target Area | Technique Notes | Avoid If).
5. End with a paragraph on return-to-sport mobility standards and how to progress toward full {sport} training.

Emphasise safety throughout. Make the plan specific to {sport} movement demands.
""",
            }

            selected_prompt = prompts.get(
                feature, prompts["1. Full-Body Workout Plan for [Position] in [Sport]"]
            )

            with st.spinner("🤖 CoachBot is creating your personalised plan..."):
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    generation_config={
                        "temperature": temperature,
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 8192,
                    }
                )
                result = get_ai_response(model, selected_prompt)

            # ── Display output ────────────────
            st.markdown("---")
            st.markdown("## 📋 Your Personalized Plan")
            st.markdown('<div class="output-box">', unsafe_allow_html=True)
            st.markdown(result)
            st.markdown("</div>", unsafe_allow_html=True)

            # ── Reference tables ──────────────
            if show_tables:
                display_tabular_dashboard(feature, training_intensity, calorie_goal)

            # ── History + download ────────────
            st.session_state.chat_history.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "feature":   feature,
                "response":  result,
            })
            st.download_button(
                "📥 Download Plan as Text File",
                data=result,
                file_name=f"coachbot_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
            )
            st.success("✅ Plan generated! Review carefully and consult a coach if needed.")

        # ── Chat history ──────────────────────
        if st.session_state.chat_history:
            st.markdown("---")
            with st.expander("📜 View Previous Plans"):
                for entry in reversed(st.session_state.chat_history[-5:]):
                    st.markdown(f"**{entry['timestamp']}** — {entry['feature']}")
                    st.text(entry["response"][:200] + "...")
                    st.markdown("---")

    # ══════════════════════════════════════════
    # TAB 2 — CUSTOM COACH
    # ══════════════════════════════════════════
    with tab2:

        st.subheader("🧠 Custom Coach Consultation")
        st.markdown(
            '<div class="feature-box">'
            "Ask any specific coaching question. Your full athlete profile from the sidebar "
            "is automatically included — the AI will tailor every answer to <strong>you</strong>."
            "</div>",
            unsafe_allow_html=True,
        )

        user_query = st.text_area(
            "Ask a specific coaching question:",
            placeholder="e.g. Suggest 3 drills for explosive speed for my position.",
            height=130,
        )

        col_a, col_b = st.columns([1, 2])
        with col_a:
            intensity_val = st.slider("Advice Intensity", 1, 100, 40)
            ai_temp       = intensity_val / 100.0
            st.caption(f"Temperature: **{ai_temp:.2f}** — higher = more creative answers")
        with col_b:
            st.info(
                "💡 **Tip:** The AI already knows your sport, position, age, fitness level, "
                "injury history and diet from the sidebar. Just ask your question naturally!"
            )

        if st.button("🎯 Ask AI Coach", type="primary"):
            if not user_query.strip():
                st.warning("Please type a question before submitting.")
            else:
                custom_prompt = f"""
You are a professional sports coach and fitness expert. Answer the question below using the athlete's full profile.

Athlete Profile:
- Name: {user_name if user_name else 'Athlete'}
- Age: {user_age} years old
- Gender: {user_gender}
- Sport: {sport}
- Position: {position}
- Fitness Level: {fitness_level}
- Injury History: {injury_history if injury_history else 'None'}
- Diet Type: {diet_type}
- Food Allergies: {allergies if allergies else 'None'}
- Calorie Goal: {calorie_goal}

Question: {user_query}
Advice Intensity: {intensity_val}/100

Write your response like this:
1. Start with 1-2 paragraphs of personalised advice that directly answers the question. Reference the athlete's sport, position, age, and any relevant injury history naturally in the text.
2. Then provide a Markdown table with structured data, drills, steps, or breakdowns relevant to the question (use appropriate columns for the topic).
3. End with 1 short paragraph of key tips or reminders specific to this athlete.

Be conversational but expert. Do not use HTML tags. Reference the athlete's profile details throughout your answer.
"""
                with st.spinner("🤖 Consulting your AI Coach..."):
                    custom_model = genai.GenerativeModel(
                        "gemini-2.5-flash",
                        generation_config={
                            "temperature": ai_temp,
                            "max_output_tokens": 2048,
                        },
                    )
                    answer = get_ai_response(custom_model, custom_prompt)

                st.markdown("---")
                st.markdown("### 📋 AI Coach Response")
                st.markdown('<div class="output-box">', unsafe_allow_html=True)
                st.markdown(answer)
                st.markdown("</div>", unsafe_allow_html=True)

                # Reference tables
                st.markdown("---")
                st.markdown("### 📊 Your Training Reference Tables")
                rc1, rc2 = st.columns(2)
                with rc1:
                    st.markdown("**📅 Weekly Schedule**")
                    st.dataframe(create_weekly_training_table("Moderate"),
                                 use_container_width=True, hide_index=True)
                with rc2:
                    st.markdown("**📈 Training Distribution**")
                    st.dataframe(create_training_distribution_table(),
                                 use_container_width=True, hide_index=True)

                st.download_button(
                    "📥 Download Response",
                    data=answer,
                    file_name=f"coachbot_custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                )

# ─────────────────────────────────────────────
# NOT CONFIGURED STATE
# ─────────────────────────────────────────────
else:
    st.info("👈 Please enter your Gemini API Key in the sidebar to get started.")
    st.markdown("### 🚀 Getting Started")
    st.markdown("""
1. **Get your API Key** — visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Enter the API Key** — paste it in the sidebar
3. **Fill your profile** — sport, position, fitness level, diet
4. **Choose a feature** — select one of 10 coaching options
5. **Generate your plan** — receive a personalised plan with text explanations and tables!
    """)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
**🏋️ Training Plans**
- Full-body workouts
- Recovery schedules
- Warm-up & cooldown
- Mobility workouts
        """)
    with c2:
        st.markdown("""
**🎯 Tactical Coaching**
- Position-specific tips
- Decision-making drills
- Mental focus techniques
- Pre-match visualisation
        """)
    with c3:
        st.markdown("""
**🍽️ Nutrition & Recovery**
- Weekly meal plans
- Hydration strategies
- Post-injury mobility
- Tournament preparation
        """)
    st.info("📊 Every plan includes written explanations AND organised tables for easy tracking!")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#666;padding:2rem 0;'>
    <p><strong>CoachBot AI</strong> — Empowering Young Athletes with AI-Powered Coaching</p>
    <p style='font-size:0.9rem;'>⚠️ Disclaimer: This AI provides general guidance. Always consult qualified coaches,
    trainers, and medical professionals before starting any new training programme.</p>
</div>
""", unsafe_allow_html=True)

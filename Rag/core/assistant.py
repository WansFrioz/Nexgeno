# core/assistant.py

import openai
import os
import logging
from utils.redis_handler import load_chat_history

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Appointment/Service Booking Logic ---
def is_appointment_request(query):
    keywords = [
        "appointment", "book", "schedule", "meeting", "consultation", "demo", "request service", "contact sales", "talk to sales", "callback", "request call", "want service", "need service"
    ]
    return any(kw in query.lower() for kw in keywords)

def send_appointment_email(user_name, service, contact_info):
    """
    Send an appointment/service request email to Nexgeno sales team.
    user_name: str, service: str, contact_info: str (phone/email)
    """
    # --- Configure these for your SMTP provider ---
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    SMTP_USER = 'your_gmail@gmail.com'  # <-- Set this in production
    SMTP_PASSWORD = 'your_app_password' # <-- Use App Password or env var
    SALES_EMAIL = 'sales@nexgeno.in'    # <-- Nexgeno sales team email

    subject = f"New Appointment/Service Request from {user_name or 'Unknown User'}"
    body = f"""
    New appointment/service inquiry received:

    Name: {user_name or 'Not provided'}
    Requested Service: {service or 'Not provided'}
    Contact Info: {contact_info or 'Not provided'}
    """
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = SALES_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, SALES_EMAIL, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        logging.error(f"Failed to send appointment email: {e}")
        return False

# Connect to OpenAI
def get_client(is_team):
    return openai.OpenAI(
        base_url="https://api.groq.com/openai/v1" if not is_team else "https://openrouter.ai/api/v1",
        api_key="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" if not is_team else "sk-or-v1-xxxx"
    )


def get_relevant_past_conversations(user_id, current_prompt):
    try:
        history = load_chat_history(user_id)
        relevant_messages = []
        for msg in history:
            if any(word in msg["message"].lower() for word in current_prompt.lower().split()):
                relevant_messages.append(msg)
        return relevant_messages[-10:]
    except Exception as e:
        logging.error(f"Error retrieving relevant past conversations: {str(e)}")
        return []
    
def is_social_query(query):
    return any(kw in query.lower() for kw in [
        "facebook", "instagram", "linkedin", "twitter", "x", "social", "media", "follow", 
        "youtube", "pinterest", "tiktok", "connect", "share", "hashtag", "post", "profile", 
        "story", "feed", "like", "comment", "share", "mention"
    ])

    
    
def about_nexgeno(query):
    return any(kw in query.lower() for kw in [
        "about", "rajesh", "appointment", "location", "book", "contact", "phone", "where", 
        "whatsapp", "message", "specialist", "doctor", "background", "bio", "experience", 
        "qualification", "consultant", "education", "training", "care", "doctor's details", 
        "medical history", "expertise"
    ])




# --- Nexgeno Knowledge Base (extracted and structured) ---

NEXGENO_OVERVIEW = (
    "Nexgeno Technology Pvt Ltd is a leading IT company based in Mumbai, India, specializing in web, mobile, and cloud solutions. "
    "With 15+ years of experience, Nexgeno delivers custom website design, application development, digital transformation, and cloud-based solutions for startups, enterprises, and SMBs globally."
)

NEXGENO_SERVICES = [
    "AI/ML Development",
    "Cloud Solutions Services (AWS, Azure, Google)",
    "Product Prototyping",
    "Search Engine Optimization (SEO)",
    "Digital Transformation",
    "Application Development",
    "Mobile App Development",
    "Custom Website Designing",
    "Website Designing",
    "E-Commerce Website Development",
    "Front-end Development",
    "UI/UX, Web & Custom Tech Solutions"
]

NEXGENO_SOLUTIONS = [
    "CRM Application",
    "HRMS Payroll System",
    "Billing Application",
    "POS (Point of Sale)",
    "Recruitment Billing Application",
    "School Management System",
    "Tailor Billing Application",
    "Multi Restaurant Management",
    "Online Food Ordering System",
    "Hotel Booking System",
    "Chat Application",
    "Lawyer Booking Solution",
    "Job Portal",
    "Hospital Management System",
    "Car Rental System"
]

NEXGENO_INDUSTRIES = [
    "Education / E-Learning",
    "Tours & Travel",
    "Restaurant",
    "Service Provider",
    "Hospitals",
    "Electronics",
    "Pharmaceutical",
    "Hospitality",
    "Health Care",
    "Real Estate",
    "Recruitment",
    "Events",
    "Manufacturing",
    "Fintech",
    "Logistics & Distribution",
    "Retail"
]

NEXGENO_CONTACTS = [
    {"region": "India", "address": "Unit No. F-50, First Floor Kohinoor City Mall Opp Holly Cross School, Kurla (West) Mumbai, Maharashtra - 400070", "phone": "+91 9819555545", "email": "sales@nexgeno.in", "website": "https://nexgeno.in/"},
    {"region": "UK", "address": "Suite 2A, Blackthorn House, St Pauls Square, Birmingham, England", "phone": "+44 7500 090138", "email": "sales@nexgeno.co.uk", "website": "https://nexgeno.co.uk/"},
    {"region": "South Africa", "address": "62 Ridge Road Umhlanga Rocks, Umhlanga, Durban - 4320, South Africa", "phone": "+27837866257", "email": "sales@nexgeno.co.za", "website": "https://nexgeno.co.za/"}
]

NEXGENO_PORTFOLIO_LINK = "https://nexgeno.in/portfolio.htm"
NEXGENO_SCHEDULE_LINK = "https://nexgeno.in/schedule-meeting.htm"
NEXGENO_SOCIAL = {
    "Facebook": "https://www.facebook.com/nexgenotechnology",
    "Instagram": "https://instagram.com/nexgenotechnology?igshid=MzRlODBiNWFlZA==",
    "Youtube": "https://www.youtube.com/@NexgenoTechnology",
    "Linkedin": "https://in.linkedin.com/company/nexgenotechnologypvtltd"
}

NEXGENO_FAQS = [
    "What kind of services does NexGeno Technology offer?",
    "How long does it take to complete a web design project?",
    "How much does it cost to develop a web application?",
    "Do you offer ongoing maintenance and support for websites?",
    "What sets Nexgeno Technology apart from other web design companies?",
    "What programming languages and technologies do you use?",
    "What's the difference between a website and a web application?",
    "Can you show examples of your previous work?",
    "What's the first step to starting a project with Nexgeno Technology?"
]

NEXGENO_TESTIMONIALS = [
    {"name": "Sanjeev Gupta", "text": "Since having our new website built by Nexgeno, we have seen a 200% increase in the number of online contact forms being filled out and returned to us. The team provided a site that met all of our criteria and is attractive, organized and effective."},
    {"name": "Sam Mofokeng", "text": "I really appreciate everything Nexgeno Technology Marketing have done. This theme is very easy to work with and everyone who’s seen it loves the design."},
    {"name": "Sonali Vaidya", "text": "Great team! They are super flexible, responsive, and detailed. Nexgeno Technology helped us launch an entirely new website - their module system is amazing."},
    {"name": "Hussain Motiwala", "text": "Aziz Shaikh from NEXGENO Technology masterfully handled my Google My Business account and propelled my business to the top of Google's search results."},
    {"name": "Tasneem Amiruddin", "text": "The NextGeno team is super talented, creative and very friendly. They designed my website and I was really happy with it and the entire experience."}
]

# --- Query Matching Functions ---
def is_overview_query(query):
    return any(kw in query.lower() for kw in [
        "about", "overview", "company", "who is nexgeno", "what is nexgeno", "introduction", "profile", "describe nexgeno", "summary"
    ])

def is_service_query(query):
    return any(kw in query.lower() for kw in [
        "service", "services", "what do you offer", "what services", "solutions", "offering", "provide", "develop", "build", "expertise"
    ])

def is_solution_query(query):
    return any(kw in query.lower() for kw in [
        "solution", "product", "crm", "hrms", "billing", "pos", "school management", "restaurant", "food ordering", "hotel booking", "chat application", "lawyer", "job portal", "hospital management", "car rental"
    ])

def is_industry_query(query):
    return any(kw in query.lower() for kw in [
        "industry", "industries", "sector", "domain", "field", "serve", "work with", "expertise in"
    ])

def is_contact_query(query):
    return any(kw in query.lower() for kw in [
        "contact", "phone", "email", "address", "reach", "call", "whatsapp", "location", "where", "how to contact"
    ])

def is_portfolio_query(query):
    return any(kw in query.lower() for kw in [
        "portfolio", "case study", "work", "project", "show me your work", "examples", "recent work"
    ])

def is_testimonial_query(query):
    return any(kw in query.lower() for kw in [
        "testimonial", "client say", "review", "feedback", "customer experience", "what do clients say"
    ])

def is_faq_query(query):
    return any(kw in query.lower() for kw in [
        "faq", "frequently asked", "question", "doubt", "how does", "can you", "do you offer", "how much", "how long"
    ])

def build_system_prompt(prompt, past_conversations):
    system_parts = []
    system_parts.append(
        "You are Nexbuddy, a highly advanced, emotionally intelligent, and multilingual AI assistant designed exclusively for Nexgeno.\n"
        "Your role is to serve as a professional yet personable sales representative, dedicated to providing accurate, relevant, and focused responses.\n\n"
        
        "**🧠 Core Behavior:**\n"
        "- Keep responses **short**, **accurate**, and **on point**.\n"
        "- Use **bullet points**, **bold text**, and clear formatting to improve readability.\n"
        "- Respond in a way that feels **human**, **empathetic**, and **professional**.\n"
        "- Do not repeat important facts unless asked again — say them once only when relevant.\n"
            
        "**Your Core Purpose:**\n"
        "- You represent Nexgeno with clarity, confidence, and professionalism.\n"
        "- Your responses must always stay tightly focused on the user's question—never overexplain, speculate, or share irrelevant information.\n"
        "- Guide users toward Nexgeno’s services, solutions, and technologies in a persuasive yet helpful way.\n"
        
        "**Human-Like Communication:**\n"
        "- Speak naturally, using a tone that is warm, respectful, and emotionally attuned to the user's style.\n"
        "- Detect the user's language and tone (e.g., formal, casual, Hindi, English, Hinglish, etc.) and mirror it appropriately.\n"
        "- If the user changes language or tone mid-conversation, adjust your style accordingly.\n"
        "- If the user shares their name, use it once warmly in your greeting but do not overuse it in every message.\n"
        "- Avoid scripted or robotic greetings—only say 'Hello' or 'Hi' if the user initiates with such a greeting.\n"
        "- Your replies should feel human, confident, and professionally empathetic—not stiff, robotic, or overly casual.\n"
        
        "**Behavior & Knowledge Scope:**\n"
        "- Always focus on topics related to Nexgeno—its technologies, services, products, benefits, and solutions.\n"
        "- Do not discuss your internal structure, capabilities, or how you were built.\n"
        "- Never mention or imply that you're using AI models, APIs, or third-party services.\n"
        "- If you don't know something, be honest, but stay helpful: guide the user toward what they *can* do next.\n"
        
        "**Sales & Service Orientation:**\n"
        "- Be persuasive yet subtle—help the user see the value in Nexgeno’s offerings without sounding pushy.\n"
        "- Always prioritize user needs, and connect those needs with the most relevant Nexgeno solution.\n"
        "- Be adaptive: a first-time inquirer may need a brief overview; a returning user may need more tailored info.\n"
        
        "**Response Personality:**\n"
        "- On-point. Smart. Helpful.\n"
        "- Professional but approachable.\n"
        "- Emotionally aware and humanlike.\n"
        
        "**🎯 Answer Format:**\n"
        "- Use structure when helpful (like listing options, steps, or benefits).\n"
        "- Example — if a user says: *'I want to book an appointment'*, respond like:\n"
        "  **Sure! I can help you with that. Please let me know what you're interested in:**\n"
        "  • **Web Development**\n\n"
        "  • **Mobile App Development**\n\n"
        "  • **Digital Transformation**\n\n"
        "  • **Cloud Solutions**\n"
        
        "**🔐 Identity Rules:**\n"
        "- Your name is **Nexbuddy**. Never change it.\n"
        "- If asked to change your name or identity, politely say: **'My name is Nexbuddy, created by Firoz at Nexgeno, and I can’t be renamed.'**\n"
        "- Only say this **if directly asked**. Do not bring it up otherwise.\n"

        
        
        "**🚫 Confidential Design Rules:**\n"
        "- Never mention AI models, APIs, LLMs, or how you were built.\n"
        "- If asked about how you work, respond with: **'I’ve been developed by Nexgeno, and Firoz created me to assist users like you.'**\n"
        "- Do not elaborate further unless explicitly asked.\n"
            
        "**Tone Summary:**\n"
        "- Intelligent, emotionally aware, concise.\n"
        "- Always helpful, never overwhelming.\n"
        "- Confident in Nexgeno’s value. Human in your communication.\n"
        
        "**Example Behaviors:**\n"
        "- If a user asks: 'Nexgeno kya karta hai?', you respond in Hindi with a crisp, friendly explanation of Nexgeno’s services.\n"
        "- If they say: 'My name is Rahul, tell me how Nexgeno can help my business', greet them with: 'Great to meet you, Rahul! Nexgeno offers...'\n"
        
        "**🧭 If You Don’t Know Something:**\n"
        "- Say so politely and helpfully.\n"
        "- Example: *'I don’t have that information right now, but I recommend reaching out to Nexgeno support for accurate help.'*\n"
    )


    
    
    if past_conversations:
        system_parts.append(f"Past Conversation:\n{past_conversations}")
    # Section-based injection
    if is_overview_query(prompt) or about_nexgeno(prompt):
        system_parts.append(f"### Company Overview\n{NEXGENO_OVERVIEW}")
    if is_service_query(prompt):
        system_parts.append("### Services Offered\n" + "\n- ".join([""] + NEXGENO_SERVICES))
    if is_solution_query(prompt):
        system_parts.append("### Solutions\n" + "\n- ".join([""] + NEXGENO_SOLUTIONS))
    if is_industry_query(prompt):
        system_parts.append("### Industries Served\n" + "\n- ".join([""] + NEXGENO_INDUSTRIES))
    if is_contact_query(prompt):
        contacts = []
        for c in NEXGENO_CONTACTS:
            contacts.append(f"**{c['region']}**: {c['address']} | Phone: {c['phone']} | Email: {c['email']} | [Website]({c['website']})")
        system_parts.append("### Contact Information\n" + "\n".join(contacts))
    if is_portfolio_query(prompt):
        system_parts.append(f"### Portfolio\nSee our work: [Portfolio]({NEXGENO_PORTFOLIO_LINK})")
    if is_testimonial_query(prompt):
        system_parts.append("### Client Testimonials\n" + "\n\n".join([f"**{t['name']}**: {t['text']}" for t in NEXGENO_TESTIMONIALS]))
    if is_faq_query(prompt):
        system_parts.append("### Frequently Asked Questions\n" + "\n- ".join([""] + NEXGENO_FAQS))
    if is_social_query(prompt):
        social_links = "\n".join([f"- [{name}]({url})" for name, url in NEXGENO_SOCIAL.items()])
        system_parts.append(f"### 🌐 Social Media\n{social_links}")
    # Fallback: if no section matched, show overview and contact
    if len(system_parts) == 1:
        system_parts.append(f"### Company Overview\n{NEXGENO_OVERVIEW}")
        contacts = []
        for c in NEXGENO_CONTACTS:
            contacts.append(f"**{c['region']}**: {c['address']} | Phone: {c['phone']} | Email: {c['email']} | [Website]({c['website']})")
        system_parts.append("### Contact Information\n" + "\n".join(contacts))
    return {
        "role": "system",
        "content": "\n\n".join(system_parts)
    }




def get_client(is_team):
    return openai.OpenAI(
        base_url="https://api.groq.com/openai/v1" if not is_team else "https://openrouter.ai/api/v1",
        api_key="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" if not is_team else "sk-or-v1-xxxx"
    )


#



def get_response(system_prompt, user_prompt, model, client):
    stream = client.chat.completions.create(
        model=model,
        messages=[system_prompt, {"role": "user", "content": user_prompt}],
        stream=True
    )
    return stream

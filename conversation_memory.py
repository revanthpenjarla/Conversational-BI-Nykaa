conversations = {}

def get_history(session_id):
    return conversations.get(session_id, [])

def add_to_history(session_id, user_prompt, sql):
    if session_id not in conversations:
        conversations[session_id] = []
    
    conversations[session_id].append(f"User: {user_prompt} | SQL: {sql}")
    
    # Keep only last 5 turns
    if len(conversations[session_id]) > 5:
        conversations[session_id] = conversations[session_id][-5:]

def clear_history(session_id):
    if session_id in conversations:
        del conversations[session_id]

if __name__ == "__main__":
    add_to_history("user1", "Show revenue by campaign type", "SELECT Campaign_Type, SUM(Revenue) FROM campaigns GROUP BY Campaign_Type")
    add_to_history("user1", "Filter only Social Media", "SELECT Campaign_Type, SUM(Revenue) FROM campaigns WHERE Campaign_Type='Social Media' GROUP BY Campaign_Type")
    
    print(get_history("user1"))
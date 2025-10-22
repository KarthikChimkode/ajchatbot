import json
from difflib import get_close_matches

# --- Load Categories and Services ---
try:
    with open("lawfeat_services.json", "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    print("❌ Error: 'your_file.json' not found. Please add your categories and services file.")
    exit()


# --- Build Service Index for Search Mode ---
all_services = []
for category in data:
    for service in category.get("services", []):
        all_services.append({
            "category": category["name"],
            "serviceName": service["serviceName"],
            "rate": service.get("rate", "N/A")
        })


# --- Helper Functions ---
def list_categories():
    """Display all categories"""
    print("\n📁 Available Categories:")
    for idx, cat in enumerate(data):
        print(f"{idx + 1}. {cat['name']}")
    return len(data)


def list_services(category_index):
    """Display services in a category"""
    category = data[category_index]
    services = category.get("services", [])
    if not services:
        print(f"\n⚠️ No services found under '{category['name']}'")
        return []
    
    print(f"\n🛠️ Services under '{category['name']}':")
    for idx, svc in enumerate(services):
        rate = svc.get("rate", "N/A")
        print(f"{idx + 1}. {svc['serviceName']} - ₹{rate}")
    return services


def post_job(selected_category, selected_service):
    """Collect job details and save"""
    print("\n📋 Let's gather some job details:")
    name = input("👤 Your Name: ").strip()
    phone = input("📞 Phone Number: ").strip()
    address = input("📍 Address: ").strip()
    date = input("📅 Preferred Date (YYYY-MM-DD): ").strip()
    time = input("⏰ Preferred Time (e.g., 10:00 AM): ").strip()

    job = {
        "category": selected_category["name"] if isinstance(selected_category, dict) else selected_category,
        "service": selected_service["serviceName"],
        "rate": selected_service.get("rate", "N/A"),
        "customer": {"name": name, "phone": phone, "address": address},
        "preferredDate": date,
        "preferredTime": time
    }

    try:
        with open("posted_jobs.json", "r", encoding="utf-8") as f:
            jobs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        jobs = []

    jobs.append(job)

    with open("posted_jobs.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

    print("\n✅ Job posted successfully!")


def find_service(user_input):
    """Find best matching services for user's text"""
    service_names = [s["serviceName"] for s in all_services]
    matches = get_close_matches(user_input, service_names, n=20, cutoff=0.4)

    if not matches:
        print("\n❌ Sorry, I couldn’t find any matching service. Try rephrasing (e.g., 'AC repair', 'bike wash').")
        return None

    print("\n🔍 I found the following matches:")
    for i, m in enumerate(matches, start=1):
        svc = next(s for s in all_services if s["serviceName"] == m)
        print(f"{i}. {svc['serviceName']} — ₹{svc['rate']} ({svc['category']})")

    choice = input("\n👉 Select a service number (or type 'none' to cancel): ").strip().lower()
    if choice == 'none':
        return None

    if not choice.isdigit() or not (1 <= int(choice) <= len(matches)):
        print("❌ Invalid choice.")
        return None

    selected_name = matches[int(choice) - 1]
    return next(s for s in all_services if s["serviceName"] == selected_name)


# --- Main Chatbot Flow ---
print("🤖 Welcome to AceJobber Smart Assistant!")
print("💬 You can either:")
print("   1️⃣ Type what you need (e.g., 'clean my sofa', 'fix AC') — Smart Mode")
print("   2️⃣ Or browse manually — Menu Mode")

while True:
    mode = input("\n🧭 Choose mode (type 'smart' or 'manual', or 'exit' to quit): ").strip().lower()

    if mode == 'exit':
        print("👋 Goodbye!")
        break

    # SMART SEARCH MODE
    elif mode == 'smart':
        user_input = input("\n💬 What service do you need? ").strip().lower()
        service = find_service(user_input)
        if not service:
            continue

        confirm = input(f"\n🛠️ Do you want to book '{service['serviceName']}' under {service['category']}? (yes/no): ").strip().lower()
        if confirm == 'yes':
            post_job({"name": service["category"]}, service)
        else:
            print("✅ Okay, not booking this one.")

    # MANUAL MENU MODE
    elif mode == 'manual':
        total_categories = list_categories()
        choice = input("\n👉 Select a category number (or type 'back' or 'exit'): ").strip().lower()
        if choice == 'exit':
            print("👋 Goodbye!")
            break
        if choice == 'back':
            continue

        if not choice.isdigit() or not (1 <= int(choice) <= total_categories):
            print("❌ Invalid category. Try again.")
            continue

        category_index = int(choice) - 1
        services = list_services(category_index)
        if not services:
            continue

        svc_choice = input("\n👉 Select a service number (or type 'back' to go back): ").strip().lower()
        if svc_choice == 'back':
            continue

        if not svc_choice.isdigit() or not (1 <= int(svc_choice) <= len(services)):
            print("❌ Invalid service. Try again.")
            continue

        service_index = int(svc_choice) - 1
        selected_category = data[category_index]
        selected_service = services[service_index]

        post_job(selected_category, selected_service)

    else:
        print("❌ Invalid option. Please type 'smart' or 'manual'.")

    next_action = input("\n🔁 Do you want to do another action? (yes/no): ").strip().lower()
    if next_action != 'yes':
        print("👋 Goodbye!")
        break

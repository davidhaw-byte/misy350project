## Structural Refactor Plan

Date: 2026-05-08
Time: 5pm

### Goal
Refactor the current Streamlit app into a layered, maintainable architecture that separates UI, service, and database responsibilities, then convert service and database logic into object-oriented classes and methods while keeping the main app entry point in `app.py`.

### Architecture
- `app.py`: main routing, session state, and high-level page control
- `ui.py`: Streamlit presentation and page rendering functions
- `services.py`: business logic and appointment workflows
- `database.py`: JSON persistence, loading, and saving data

### Refactor Strategy
1. Backup `users.json` and `appointments.json`.
2. Move JSON file operations from `app.py` into `database.py`.
3. Move authentication and appointment workflows into `services.py`.
4. Move Streamlit UI code into `ui.py` and keep `app.py` for navigation.
5. Introduce model classes: `User` and `Appointment`.
6. Refactor procedural functions into class methods.
7. Keep UI, service, and data layers separated.
8. Validate that login, registration, booking, cancellation, and doctor updates continue working.

### Object-Oriented Focus
- `User`: represent user data and role helpers
- `Appointment`: represent appointments with `book()`, `cancel()`, `reschedule()`, and status helpers
- `AuthService`: handle `login()`, `register()`, and `logout()`
- `AppointmentService`: handle appointment queries and workflow methods
- `DatabaseManager`: encapsulate JSON load/save operations

### Original Prompt
Now I want you to create a plan for the structural changes. This plan should focus on improving organization, layering, maintainability, and seperation of concerns. It should put the UI functions into a UI file, the service functions into a services file, and the database functions into a database file, while keeping the main functions in the main file. After seperation focus should be turned to changing the functions into object oriented programming. Creating objects and functions lying within them. The original prompt should be put into the origin prompt file as well as included in the plan. Also record data and time of the plan. Remember the importance of the phase 2 instructions, layering, and object oriented programming in this plan to revise the structure.

### Implementation Review
- `app.py`: converted to the main routing entry point only.
- `ui.py`: created to host all Streamlit UI rendering, input forms, navigation buttons, and page layouts.
- `data/models.py`: created `User` and `Appointment` classes with serialization methods and behavior helpers.
- `data/database.py`: created `DatabaseManager` to load/save JSON files and retrieve user/appointment records.
- `services/auth_service.py`: created `AuthService` for login and registration, including password hashing and compatibility for existing passwords.
- `services/appointment_service.py`: created `AppointmentService` for booking, cancelling, rescheduling, creating availability, and status updates.
- `services/chat_service.py`: added `AIChatService` for assistant responses, with OpenAI support and a fallback conversational helper.
- `requirements.txt`: updated to include `streamlit`, `bcrypt`, `openai`, and `python-dotenv`.
- `users_backup.json` and `appointments_backup.json`: created backup copies of the existing JSON data before refactoring.

### Layer Interaction Notes
- UI layer (`ui.py`) now calls service methods instead of performing business logic directly, so presentation is separated from process rules.
- Service layer (`services/*.py`) now uses database methods and model objects, so appointment rules and authentication are separated from raw JSON access.
- Database layer (`data/database.py`) is isolated from Streamlit and user session state, so persistence is handled independently of UI behavior.
- Model layer (`data/models.py`) supports service behavior with object methods like `book()`, `cancel()`, and `reschedule()`, reducing raw dictionary mutation.


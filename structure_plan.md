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

## Simplified Layer Refinement Plan

Date: 2024-12-19  
Time: 11:30 AM  

### Goal
Ensure crystal-clear separation of concerns across the three core layers (UI, Service, Data) without adding unnecessary infrastructure. Focus on making the existing architecture more maintainable and testable.

### Current Three-Layer Architecture
1. **UI Layer** (`ui.py`): All Streamlit rendering and user interaction
2. **Service Layer** (`services/`): Business logic, validation, and orchestration
3. **Data Layer** (`data/`): Models and persistence

### Layer Separation Principles

#### UI Layer (`ui.py`) - What It Should Do
- **Only**: Render components, handle user input, display feedback, manage page routing
- **Never**: 
  - Perform database operations directly
  - Contain business logic or validation rules
  - Access JSON files
  - Have hardcoded appointment status checks or authentication logic
- **Best Practice**: Call service methods and display results; let services handle logic

#### Service Layer (`services/`) - What It Should Do
- **Only**: Implement business logic, validate data, orchestrate operations, raise domain errors
- **Components**:
  - `AuthService`: Login, registration, password handling
  - `AppointmentService`: Booking, cancellation, status updates, availability
  - `AIChatService`: Chat responses and context building
- **Never**:
  - Directly access or manipulate UI elements
  - Include Streamlit imports (except in type hints)
  - Store Streamlit session state
  - Make hardcoded UI decisions
- **Best Practice**: Accept parameters, return results or errors; services are reusable and testable

#### Data Layer (`data/`) - What It Should Do
- **Only**: Model definition, serialization, persistence operations
- **Components**:
  - `models.py`: `User` and `Appointment` dataclasses with helpers
  - `database.py`: `DatabaseManager` for JSON operations
- **Never**:
  - Contain business rules or validation logic
  - Know about Streamlit
  - Make decisions about appointment workflows
  - Include service-level orchestration
- **Best Practice**: Pure data operations; no side effects or complex logic

### Refinement Focus Areas

#### 1. Clean Imports
- **Ensure**: Services do not import from `ui.py`
- **Ensure**: Data layer does not import services
- **Ensure**: UI layer imports services and data, but only for instantiation

#### 2. Clear Method Contracts
- **Services**: Return tuples `(result, error)` or simple types; raise exceptions only for critical failures
- **Database**: Accept model objects, return model objects or None; handle I/O errors internally
- **UI**: Accept service methods and session state; pass parameters to services

#### 3. No Logic Leakage
- **Common Anti-Pattern**: Business logic in UI (e.g., status validation in `st.selectbox`)
- **Solution**: Move all logic to service layer; UI only calls methods
- **Example**: Appointment cancellation should be validated in `AppointmentService.cancel()`, not in `ui.render_cancel_button()`

#### 4. Type Consistency
- **Use consistent return types**: Services return `(object, error_string)` pairs
- **Use model objects**: Pass `User` and `Appointment` objects, not dictionaries
- **Document assumptions**: Comment on expected data formats

### Implementation Checklist
- [ ] UI layer: No database imports, all business logic delegated to services
- [ ] Service layer: No Streamlit imports, all logic is self-contained and testable
- [ ] Data layer: Models and persistence only, no business logic
- [ ] Method signatures: Clear contracts with consistent return types
- [ ] Error handling: Services return error tuples; critical errors raise exceptions
- [ ] Test-readiness: Services can be tested without UI or database mocks

### Why This Matters
- **Maintainability**: Changes to business logic don't require UI tweaks
- **Reusability**: Services can be used by different UIs (CLI, API, etc.)
- **Testability**: Services can be unit tested without Streamlit
- **Debugging**: Clear layer boundaries make it easier to isolate issues

### Original Prompt
Please redo the plan and document the new plan. The previous plan added un needed layers. We want to just keep it to the ui, data and service layer. The goal of this plan is not to overdo the made changes but to ensure their is a clear distinction between layers.


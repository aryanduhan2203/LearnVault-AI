from app.database import supabase


class AuthService:

    def register(self, email: str, password: str):
        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            return {
                "message": "Registration successful. Check your email if confirmation is required.",
                "user": response.user,
                "session": response.session
            }

        except Exception as error:
            raise ValueError(str(error))

    def login(self, email: str, password: str):
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            return {
                "message": "Login successful",
                "user": response.user,
                "session": response.session
            }

        except Exception:
            raise ValueError("Invalid email or password")

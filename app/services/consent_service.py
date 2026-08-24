class ConsentService:
    @staticmethod
    def verify_consent(job_id: str, is_consented: bool) -> bool:
        """
        In a real app, this would check a database or external service.
        For now, it returns the provided boolean.
        """
        if not is_consented:
            print(f"Warning: Consent not verified for job {job_id}. Voice cloning will be disabled.")
        return is_consented

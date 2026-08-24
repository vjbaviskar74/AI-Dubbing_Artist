class ReviewService:
    @staticmethod
    def save_review(item_type: str, item_id: str, data: dict):
        # In a real app, save to database
        print(f"Saved review for {item_type} {item_id}: {data}")
        return True

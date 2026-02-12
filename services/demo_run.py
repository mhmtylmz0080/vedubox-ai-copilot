from ai_service import AIRequest, Role, UseCase, handle_ai_request

if __name__ == "__main__":
    # Instructor: Engagement analysis demo
    req = AIRequest(
        role=Role.INSTRUCTOR,
        use_case=UseCase.ENGAGEMENT_ANALYSIS,
        user_message="Modül 3'te katılım düşüyor, ne önerirsin?",
        context={
            "course_title": "CRM Eğitimi",
            "module_title": "İtiraz Yönetimi",
            "engagement_summary": "Drop-off rate 23% at module 3",
            "quiz_analysis": "Question 5 wrong rate 67%",
        },
    )
    res = handle_ai_request(req)
    print("OK:", res.ok)
    print("MESSAGE:", res.message)
    print("ACTIONS:", res.actions)
    print("META:", res.metadata)

function scrollToGroups() {
    document.getElementById("groups").scrollIntoView({ behavior: "smooth" });
}

document.addEventListener("DOMContentLoaded", () => {
    const openModal = document.getElementById("openPostModal");
    const modal = document.getElementById("postModal");
    const closeModal = document.getElementById("closePostModal");
    const cancelPost = document.getElementById("cancelPost");
    const form = document.getElementById("newPostForm");

    // Open Modal
    openModal.addEventListener("click", () => {
        modal.style.display = "block";
        document.body.style.overflow = "hidden";
    });

    // Close modal function
    const close = () => {
        modal.style.display = "none";
        document.body.style.overflow = "auto";
        form.reset();
    };

    closeModal.addEventListener("click", close);
    cancelPost.addEventListener("click", close);

    window.addEventListener("click", (e) => {
        if (e.target === modal) close();
    });

    // Submit handler
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const data = {
            group: form.group.value,
            title: form.title.value,
            content: form.content.value
        };
        console.log("Post submitted:", data);
        alert("Post created successfully!");
        close();
    });

    // Scroll reveal effect
    const reveals = document.querySelectorAll(".group-card, .post-card");
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = "1";
                entry.target.style.transform = "translateY(0)";
            }
        });
    }, { threshold: 0.2 });

    reveals.forEach(el => {
        el.style.opacity = "0";
        el.style.transform = "translateY(40px)";
        el.style.transition = "all 0.8s ease";
        observer.observe(el);
    });
});
document.addEventListener('DOMContentLoaded', () => {
    const reviewApp = Vue.createApp({
        data() {
            return {
                reviews: [],
                page: 1,
                loading: false,
                hasNext: true,
            };
        },
        methods: {
            async fetchReviews() {
                if (this.loading || !this.hasNext) return;
                this.loading = true;
                try {
                    const response = await fetch(`/api/reviews/?page=${this.page}`);
                    const data = await response.json();
                    console.log('Fetched reviews:', data.reviews);
                    this.reviews = [...this.reviews, ...data.reviews];
                    this.hasNext = data.has_next;
                    this.page += 1;
                } catch (error) {
                    console.error('Ошибка загрузки:', error);
                } finally {
                    this.loading = false;
                }
            },
            formatDateTime(dateString) {
                const options = {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',

                };
                return new Intl.DateTimeFormat('ru-RU', options).format(new Date(dateString));
            },
            truncateWords(text, length) {
                return text.length > length ? text.slice(0, length) + '...' : text;
            },
            handleScroll() {
                if (window.innerHeight + window.scrollY >= document.documentElement.offsetHeight - 100) {
                    this.fetchReviews();
                }
            },
        },
        mounted() {
            console.log('Vue приложение успешно смонтировано');
            this.fetchReviews();
            window.addEventListener('scroll', this.handleScroll);
        },
        beforeUnmount() {
            window.removeEventListener('scroll', this.handleScroll);
        },
        template: `
            <div v-if="reviews.length === 0">Нет обзоров для отображения.</div>
            <div v-else>
                <div v-for="review in reviews" :key="review.id" class="news-card">
                    <h3>{{ review.title }}</h3>
                    <p class="review-meta">
                        Автор: {{ review.author__nickname }} | Дата: {{ formatDateTime(review.created_at) }}
                    </p>
                    <p>{{ truncateWords(review.content, 140) }}</p>
                    <a :href="'/content_detail/' + review.id">Читать далее</a>
                </div>
            </div>
        `,
    });

    reviewApp.mount('#review-section');
});

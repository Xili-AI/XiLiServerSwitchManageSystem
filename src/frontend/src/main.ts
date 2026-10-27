import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './styles/tokens.css'
import './styles/global.css'
import './styles/pixel.css'
import './styles/animations.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
const auth = useAuthStore(pinia)

app.config.errorHandler = (error) => {
  console.error('[XiLi Gateway]', error)
}

auth.bootstrap().finally(() => {
  app.use(router)
  app.mount('#app')
})

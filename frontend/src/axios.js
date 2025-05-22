import axios from 'axios'
import dataService from './components/dataService'
import { useLoginStore } from '@/store'

const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_APP_AXIOS_URL
})

function urlBelongsToBase(base, url) {
  try {
    const baseUrl = new URL(base)
    const fullUrl = new URL(url, base) // allows for relative URLs too

    return baseUrl.origin === fullUrl.origin && fullUrl.pathname.startsWith(baseUrl.pathname)
  } catch (e) {
    // Invalid URL
    return false
  }
}

axiosInstance.interceptors.request.use(
  function (config) {
    const loginStore = useLoginStore()
    const token = loginStore.token

    if (urlBelongsToBase(axiosInstance.defaults.baseURL, config.url)) {
      config.headers['Authorization'] = 'Bearer ' + token
    }
    return config
  },
  function (error) {
    return Promise.reject(error)
  }
)

//Response interceptor
axiosInstance.interceptors.response.use(
  function (response) {
    const loginStore = useLoginStore()
    if (response.headers['bearer-refreshed'])
      loginStore.updateBearer(response.headers['bearer-refreshed'])

    return response
  },
  function (error) {
    const loginStore = useLoginStore()
    // Any status codes that falls outside the range of 2xx cause this function to trigger
    if (urlBelongsToBase(axiosInstance.defaults.baseURL, error.config.url)) {
      if (error.response.status == 401) {
        loginStore.removeBearer()
        dataService.logout()
        return Promise.reject(401)
      }
    }
    return Promise.reject(error)
  }
)

export default axiosInstance

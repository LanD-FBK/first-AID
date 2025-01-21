import axios from 'axios'
import dataService from './components/dataService'
import { useLoginStore } from '@/store'

const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_APP_AXIOS_URL
})

axiosInstance.interceptors.request.use(
  function (config) {
    const loginStore = useLoginStore()
    const token = loginStore.token
    //adds bearer token header only when calling baseURL APIs
    if (!String(config.url).includes('www.') && !String(config.url).includes('http'))
      config.headers['Authorization'] = 'Bearer ' + token
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
    if (error.response.status == 401) {
      console.log(error)
      //Removes expired token
      loginStore.removeBearer()
      dataService.logout()
      return Promise.reject(401)
    }
    return Promise.reject(error)
  }
)

export default axiosInstance

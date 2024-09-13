import axios from 'axios'
import dataService from './components/dataService'
import { useLoginStore } from '@/store'

const axiosInstance = axios.create({
  baseURL: 'https://dh-hetzner.fbk.eu/first-aid'
})

axiosInstance.interceptors.request.use(
  function (config) {
    const loginStore = useLoginStore()
    const token = loginStore.token
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token
    }
    return config
  },
  function (error) {
    // Do something with request error
    return Promise.reject(error)
  }
)

//Response interceptor
axiosInstance.interceptors.response.use(
  //Arrow function?
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
      //Removes expired token (interceptor doesn't send it with the next 'login' request)
      loginStore.removeBearer()
      dataService.logout()
      return Promise.reject(401)
    }
    return Promise.reject(error)
  }
)

export default axiosInstance

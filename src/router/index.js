import { createRouter, createWebHistory } from 'vue-router'

import login from '@/components/login-page.vue'
import projects from '@/components/projects-list.vue'
import changePassword from '@/components/change-password.vue'
import tasks from '@/components/task-list.vue'
import dataService from '@/components/dataService'
import test from '@/components/test.vue'
import annotationInterface from '@/components/annotation-interface.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: login
    },
    {
      path: '/projects',
      name: 'projects',
      component: projects
    },
    {
      path: '/changepassword',
      name: 'changePassword',
      component: changePassword
    },
    {
      path: '/projects/:projectID/tasks/:taskID/annotate',
      name: 'annotation',
      component: annotationInterface
    },
    {
      path: '/projects/:projectID/tasks/',
      name: 'tasks',
      component: tasks
    }
  ]
})

//Not working. TODO: redirect to 'projects' from 'login' is already authenticated
router.beforeEach((to, from) => {
  if (dataService.isAuthenticated() && (to.name == 'login' || from.name == 'login')) {
    console.log('truetrue')
    return { name: 'projects' }
  }
})

export default router

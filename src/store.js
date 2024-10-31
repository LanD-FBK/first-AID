import { defineStore } from 'pinia'

export const useLoginStore = defineStore('login', {
  state: () => ({
    token: undefined,
    username: undefined,
    is_admin: false,
    project_manager: []
  }),
  actions: {
    updateBearer(newToken) {
      this.token = newToken
    },
    removeBearer() {
      this.token = undefined
    },
    updateUser(newUsername, is_admin, project_manager) {
      this.username = newUsername
      this.is_admin = is_admin
      this.project_manager = project_manager
    },
    removeUser() {
      this.username = undefined
      this.is_admin = false
      this.project_manager = []
    },
    removeAll() {
      this.removeBearer()
      this.removeUser()
    },
    isToken() {
      if (this.token) return true
      return false
    }
  },
  persist: true
})

export const useVariablesStore = defineStore('variables', {
  state: () => ({
    //Max width used by all "primary" dialogs
    dialogMaxWidth: '700px',
    //Max width used by all warning and error dialogs
    errorMaxWidth: '350px'
  })
})

export const useNewTaskStore = defineStore('newTask', {
  state: () => ({
    initialData: [
      { complete: 'Empty', apiFormat: 'empty' },
      { complete: 'Pre-filled', apiFormat: 'pre_compiled' }
    ],
    newTurn: [
      { complete: 'Clean', apiFormat: 'clean' },
      { complete: 'Choice', apiFormat: 'choice' }
    ],
    language: [
      { complete: 'Italiano', apiFormat: 'it' },
      { complete: 'English', apiFormat: 'en' }
    ],
    //Minimum number of roles for a new task
    minimumRoles: 2,
    //v-model for the 'New Task' Dialog
    dialogNewTask: false
  }),
  actions: {
    openNewTaskDialog() {
      this.dialogNewTask = true
    },
    cloneNewTaskDialog() {
      this.dialogNewTask = false
    }
  }
})

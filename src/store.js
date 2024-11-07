import { defineStore } from 'pinia'

export const useLoginStore = defineStore('login', {
  state: () => ({
    token: undefined,
    username: undefined,
    is_admin: false,
    user_id: undefined,
    project_manager: []
  }),
  actions: {
    updateBearer(newToken) {
      this.token = newToken
    },
    removeBearer() {
      this.token = undefined
    },
    updateUser(newUsername, newUserID, is_admin, project_manager) {
      this.username = newUsername
      this.user_id = newUserID
      this.is_admin = is_admin
      this.project_manager = project_manager
    },
    removeUser() {
      this.username = undefined
      this.user_id = undefined
      this.is_admin = false
      this.project_manager = []
    },
    removeAll() {
      this.removeBearer()
      this.removeUser()
    },
    isToken() {
      return !!this.token;
    }
  },
  persist: true
})

export const useVariablesStore = defineStore('variables', {
  state: () => ({
    //Max width used by all "primary" dialogs
    dialogMaxWidth: '80%',
    //Max width used by all warning and error dialogs
    errorMaxWidth: '350px',
    rulesCreateUser: [
      function (value) {
        if (value) return true
        return 'This field cannot be empty'
      }
    ],

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
    initialTaskRoles: [
      {
        name: '',
        id: '',
        ground: false,
        number: 0
      },
      {
        name: '',
        id: '',
        ground: true,
        number: 1
      }
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

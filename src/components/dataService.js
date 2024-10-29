import axios from '../axios'
import router from '../router/index'
import { useLoginStore } from '@/store'

export default {
  logout: function () {
    const loginStore = useLoginStore()
    loginStore.removeAll()
    router.push({ name: 'login' })
  },
  getToken: function (username, password) {
    return axios.post(
      '/token',
      {
        username: username,
        password: password
      },
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )
  },

  getUsers: function () {
    return axios.get('/users/')
  },

  //Returns '201 created' if successful
  createUser: function (email, username, password) {
    return axios.post('/users/', {
      email: email,
      username: username,
      password: password
    })
  },

  editUser: function (email, username, password, userID) {
    return axios.patch(String('/users/' + userID + '/edit/'), {
      email: email,
      username: username,
      password: password
    })
  },

  //Returns '204 no content' if successful
  changePassword: function (oldPassword, newPassword) {
    return axios.patch(
      '/users/me/changepassword?old_password=' + oldPassword + '&new_password=' + newPassword
    )
  },

  /* Not working.
  changeParams: function (oldPassword, newPassword) {
    return axios.patch('/users/me/changepassword', {
      params: {
        old_password: oldPassword,
        new_password: newPassword
      }
    })
  },
  */

  changeActiveState: function (userID) {
    return axios.patch(String('/users/' + userID + '/changeactivestate/'))
  },

  deleteUser: function (userID) {
    return axios.delete('/users/' + userID)
  },

  getProjects: function () {
    return axios.get('/projects/')
  },

  //TODO: data handling
  createProject: function (name, isActive, users_list, users_manage) {
    return axios.post('/projects/', {
      name: name,
      is_active: isActive,
      users_list: users_list,
      users_manage: users_manage
    })
  },

  getProjectByID: function (projectID) {
    return axios.get(String('/projects/' + projectID))
  },

  editProject: function (projectID, name, isActive, users_list, users_manage) {
    return axios.patch('/projects/' + projectID + '/edit', {
      name: name,
      is_active: isActive,
      users_list: users_list,
      users_manage: users_manage
    })
  },

  assignUserToProject: function (projectID, userID, isAdmin) {
    return axios.put('/projects/' + projectID, {
      user_id: userID,
      user_manage: isAdmin
    })
  },

  removeUserFromProject: function (projectID, userID) {
    return axios.delete('/projects/' + projectID + '/revokeuser', {
      user_id: userID
    })
  },

  deleteProject: function (projectID) {
    return axios.delete('/projects/' + projectID)
  },

  getProjectFiles: function (projectID) {
    return axios.get('/projects/' + projectID + '/file/')
  },

  uploadFiles: function (projectID, files) {
    let form = new FormData()
    for (let file of files) {
      console.log(file)
      form.append('files', file)
      console.log(form)
    }
    return axios({
      method: 'post',
      url: '/projects/' + projectID + '/file/',
      data: form,
  })
  },

  deleteProjectFiles: function (projectID, documentID) {
    const requestBody = [documentID]
    console.log(typeof requestBody)
    return axios.delete('/projects/' + projectID + '/file/delete/', {
      data: {
        0: requestBody
      }
    })
  },

  addTaskToProject: function (
    projectID,
    taskName,
    taskStartType,
    taskInsideType,
    taskLanguage,
    taskIsActive,
    taskMeta,
    taskActorsList,
    taskUsersList,
    taskFilesList
  ) {
    return axios.post('/projects/' + projectID + '/tasks/', {
      name: taskName,
      start_type: taskStartType,
      inside_type: taskInsideType,
      language: taskLanguage,
      is_active: taskIsActive,
      meta: taskMeta,
      actors_list: taskActorsList,
      users_list: taskUsersList,
      files_list: taskFilesList
    })
  },

  getTaskInfo: function (projectID, taskID) {
    return axios.get('/projects/' + projectID + '/tasks/' + taskID)
  },

  //Not working. Is it useful?
  isAuthenticated: function () {
    axios
      .get('/users/')
      .then(function () {
        // console.log('true')
        return true
      })
      .catch(function () {
        // console.log('false')
        return false
      })
  },

  //Gets data from the endpoint specified during project creation
  getTaskData: function (endpoint) {
    return axios.get(endpoint)
  },

  deleteTask: function(projectID, taskID){
    return axios.delete('/projects/' + projectID + '/tasks/' + taskID)
  },

  activateTask: function(projectID, taskID){
    return axios.patch('/projects/' + projectID + '/tasks/' + taskID + '/activate')
  },

  deactivateTask: function(projectID, taskID){
    return axios.patch('/projects/' + projectID + '/tasks/' + taskID + '/deactivate')
  },

  //This call only works when there is no ending "slash" symbol
  getFileContent: function (projectID, fileID) {
    return axios.get('/projects/' + projectID + '/file/' + fileID + '/content')
  },

  getAllAnnotations: function(projectID, taskID){
    return axios.get('/projects/' + projectID + '/tasks/' + taskID + '/annotations')
  },

  createAnnotation: function(projectID, taskID, annotations, comment, parent){
    return axios.post('/projects/' + projectID + '/tasks/' + taskID + 'annotations', {
      annotations: annotations,
      comment: comment,
      parent: parent
    })
  },

  getAnnotation: function(projectID, taskID, annotationID){
    return axios. get('/projects/' + projectID + '/tasks/' + taskID + '/annotations/' + annotationID)
  },

  editAnnotation: function(projectID, taskID, annotationID, annotations, comment){
    return axios.patch('/projects/' + projectID + '/tasks/' + taskID + '/annotations/' + annotationID, {
        annotations: annotations,
      comment: comment
    }
    )
  },

  deleteAnnotation: function(projectID, taskID, annotationID){
    return axios.delete('/projects/' + projectID + '/tasks/' + taskID + '/annotations/' + annotationID)
  },

  closeAnnotation: function(projectID, taskID, annotationID){
    return axios.patch('/projects/' + projectID + '/tasks/' + taskID + '/annotations/' + annotationID + '/close')
  },

  reopenAnnotation: function(projectID, taskID, annotationID){
    return axios.patch('/projects/' + projectID + '/tasks/' + taskID + '/annotations/' + annotationID + '/reopen')
  },
}

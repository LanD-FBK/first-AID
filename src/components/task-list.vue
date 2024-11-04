<script>
import { useNewTaskStore, useLoginStore } from '@/store'
import dataService from './dataService'
import TaskAnnotations from '@/components/singleFileComponents/task-annotations.vue'
import TaskDialog from './singleFileComponents/task-dialog.vue';

function addChildren(obj, annotations, index) {
  if (Object.prototype.hasOwnProperty.call(annotations, index)) {
    obj.children = []
    for (let a of annotations[index]) {
      obj.children.push(a)
      addChildren(a, annotations, a.id)
    }
  }
}

export default {
  components: {
    TaskAnnotations,
    TaskDialog
  },
  emits: ['openNewProject'],
  data() {
    return {
      newTaskStore: useNewTaskStore(),
      loginStore: useLoginStore(),
      projectName: undefined,
      tasks: undefined,
      projectID: undefined,
      annotations: {},
      users: undefined,
      files: undefined,
      id: undefined
    }
  },
  mounted: function () {
    this.id = this.$route.params.projectID
    this.annotations = {}
    this.loadData()
    const self = this
    dataService.getProjectByID(this.id).then(function (data) {
      console.log(data.data)
      self.projectName = data.data.name
      self.tasks = data.data.tasks
      self.users = data.data.users
      self.files = data.data.files
      console.log(self.tasks)
    })
  },
  computed: {
    isManager: function () {
      return this.loginStore.is_admin || this.loginStore.project_manager.includes(this.projectID)
    }
  },
  methods: {
    addAnnotation: function (task_id, parent) {
      if (parent === 0) {
        this.$router.push({
          name: 'annotation',
          params: { projectID: this.projectID, taskID: task_id }
        })
      } else {
        this.$router.push({
          name: 'annotation_parent',
          params: { projectID: this.projectID, taskID: task_id, annotationParent: parent }
        })
      }
    },
    editAnnotation: function (task_id, annotation_id) {
      this.$router.push({
        name: 'annotation_edit',
        params: { projectID: this.projectID, taskID: task_id, annotationID: annotation_id }
      })
    },
    deactivateTask: function (task_id) {
      const self = this
      dataService.deactivateTask(this.projectID, task_id).then(function () {
        self.loadData()
      })
    },
    activateTask: function (task_id) {
      const self = this
      dataService.activateTask(this.projectID, task_id).then(function () {
        self.loadData()
      })
    },
    closeAnnotation: function (task_id, id) {
      const self = this
      dataService.closeAnnotation(this.projectID, task_id, id).then(function () {
        self.loadData()
      })
    },
    reopenAnnotation: function (task_id, id) {
      const self = this
      dataService.reopenAnnotation(this.projectID, task_id, id).then(function () {
        self.loadData()
      })
    },
    loadData: function () {
      const self = this
      dataService.getProjectByID(this.$route.params.projectID).then(function (data) {
        self.projectID = self.$route.params.projectID
        self.projectName = data.data.name
        self.tasks = data.data.tasks

        for (let t of data.data.tasks) {
          let new_task = {}
          new_task.id = 'task-' + t.id
          new_task.title = t.name
          // new_task.children = [];

          let tmp_annotations = {}
          for (let a of t.annotations) {
            if (!Object.prototype.hasOwnProperty.call(tmp_annotations, a.parent)) {
              tmp_annotations[a.parent] = []
            }
            tmp_annotations[a.parent].push({
              id: a.id,
              title: a.user.username,
              subtitle: a.comment,
              closed: a.closed
            })
          }

          addChildren(new_task, tmp_annotations, 0)

          self.annotations[t.id] = new_task
        }
      })
    }
  }
}
</script>

<template>
  <v-container fluid v-if="tasks === undefined">
    <v-row>
      <v-col cols="12" align="center">
        <v-progress-circular indeterminate class="mx-auto" :size="128"></v-progress-circular>
      </v-col>
    </v-row>
  </v-container>
  <v-container fluid v-else>
    <v-row justify="center">
      <v-col cols="6">
        <p class="text-h2">Project "{{ projectName }}" Tasks</p>
      </v-col>
      <v-col cols="6" align="right">
        <TaskDialog :users="this.users" :files="this.files" :projectID="Number(this.id)"></TaskDialog>
      </v-col>
    </v-row>
    <v-list lines="two">
      <!--      <v-list-subheader inset>Folders</v-list-subheader>-->

      <template v-for="task of tasks" :key="task.id">
        <v-list-item :subtitle="task.id" :title="task.name" class="mt-3 task-item">
          <template v-slot:prepend>
            <v-avatar :color="task.is_active ? 'green-lighten-1' : 'red-lighten-1'">
              <v-icon color="white">mdi-head-cog</v-icon>
            </v-avatar>
          </template>

          <template v-slot:append>
            <v-btn v-if="task.is_active" class="ms-3" color="blue-lighten-1" icon="mdi-text-box-plus"
              @click="addAnnotation(task.id, 0)"></v-btn>
            <v-btn v-if="task.is_active" class="ms-3" color="red-lighten-1" icon="mdi-lock"
              @click="deactivateTask(task.id)"></v-btn>
            <v-btn v-else class="ms-3" color="green-lighten-1" icon="mdi-lock-open-variant"
              @click="activateTask(task.id)"></v-btn>
          </template>
        </v-list-item>

        <TaskAnnotations v-if="annotations[task.id].children" :annotations="annotations[task.id].children"
          :is-manager="isManager" :task="task" @close-annotation="closeAnnotation" @reopen-annotation="reopenAnnotation"
          @add-annotation="addAnnotation" @edit-annotation="editAnnotation" :depth="50">
        </TaskAnnotations>
      </template>
    </v-list>
  </v-container>
</template>

<style scoped>
.task-item {
  /*background-color: #d1e8ca;*/
  border-top: 1px solid green;
}
</style>

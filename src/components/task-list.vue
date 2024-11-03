<script>
import { useNewTaskStore } from '@/store';
import dataService from './dataService';
import TaskItem from './singleFileComponents/task-item.vue';
import TaskDialog from './singleFileComponents/task-dialog.vue';

export default {
  components: {
    TaskItem,
    TaskDialog
  },
  data() {
    return {
      newTaskStore: useNewTaskStore(),
      projectName: undefined,
      tasks: undefined,
      users: undefined,
      files: undefined,
      id: undefined
    }
  },
  mounted: function () {
    this.id = this.$route.params.projectID
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
  methods: {

  }
}
</script>

<template>
  <v-container fluid v-if="tasks == undefined">
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
        <TaskDialog :users="this.users" :files="this.files" :projectID="this.id"></TaskDialog>
      </v-col>
    </v-row>
    <template v-for="task of tasks" :key="task.id">
      <TaskItem :taskID="task.id" :title="task.name" :isActive="task.is_active" />
    </template>
  </v-container>
</template>

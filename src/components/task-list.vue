<script>
import { useNewTaskStore } from '@/store';
import dataService from './dataService';
import TaskItem from './singleFileComponents/task-item.vue';

export default {
  components: {
    TaskItem
  },
  data(){
    return {
      newTaskStore: useNewTaskStore(),
      projectName: undefined,
      tasks: undefined
    }
  },
  mounted: function(){
    const self = this
    dataService.getProjectByID(this.$route.params.projectID).then(function(data){
      console.log(data.data)
      self.projectName = data.data.name
      self.tasks = data.data.tasks
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
    <v-container fluid>
    <v-row justify="center">
      <v-col cols="6">
        <p class="text-h2">{{ projectName }} Tasks</p>
      </v-col>
      <v-col cols="6" align="right">
        <v-btn color="primary" variant="elevated">Add Task</v-btn>
      </v-col>
    </v-row>
    <template v-for="task of tasks" :key="task.id">
      <TaskItem :taskID="task.id" :projectID="this.$route.params.projectID" :title="task.name" :isActive="task.is_active"/>
    </template>
  </v-container>
</template>

<script>
import { useVariablesStore } from '@/store'
import dataService from './dataService'
import ListItem from './singleFileComponents/list-item.vue'

export default {
  components: {
    ListItem
  },
  data() {
    return {
      variablesStore: useVariablesStore(),
      ds: dataService,
      projects: undefined,
      dialogProjectDeletion: false,
      deletingProjectID: -1,
      deletingProjectName: '',
      dialogProjectDeletionError: false,
      projectDeletionErrorMessage: ''
    }
  },
  mounted: function () {
    const self = this
    dataService.getProjects().then(function (data) {
      self.projects = data.data
    })
  },
  methods: {
    openProjectDeletionDialog: function (projectID, projectName) {
      this.deletingProjectID = projectID
      this.deletingProjectName = projectName
      this.dialogProjectDeletion = true
      console.log(this.deletingProjectID)
    },
    confirmProjectDeletion: function () {
      const self = this
      dataService
        .deleteProject(this.deletingProjectID)
        .then(function (data) {
          self.deletingProjectID = -1
          self.deletingProjectName = ''
          self.$router.go(0)
        })
        .catch(function (error) {
          self.dialogProjectDeletionError = true
          self.projectDeletionErrorMessage = String(error.message + ": " + error.response.statusText)
        })
    }
  }
}
</script>

<template>
  <v-container fluid v-if="projects == undefined">
    <v-row>
      <v-col cols="12" align="center">
        <v-progress-circular indeterminate class="mx-auto" :size="128"></v-progress-circular>
      </v-col>
    </v-row>
  </v-container>
  <v-container fluid v-else>
    <v-row justify="center">
      <v-col cols="6">
        <p class="text-h2">Projects</p>
      </v-col>
      <v-col cols="6" align="right">
        <v-btn color="primary" variant="elevated" @click="$emit('openNewProject')"
          >Add Project</v-btn
        >
      </v-col>
      <v-col cols="12" align="center"> </v-col>
    </v-row>
    <template v-for="project of projects" :key="project.id">
      <ListItem
        :title="project.name"
        :users="project.users"
        :id="project.id"
        :isActive="project.is_active"
        @deleteProject="openProjectDeletionDialog(project.id, project.name)"
      />
    </template>

    <!-- Project deletion warning dialog-->
    <v-dialog v-model="dialogProjectDeletion" :maxWidth="variablesStore.errorMaxWidth">
      <v-card
        color="warning"
        prepend-icon="mdi-alert"
        title="Are you sure?"
        :text="
          'Do you really want to delete project ' +
          deletingProjectName +
          '? This action cannot be undone'
        "
      >
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text="Back" @click="dialogProjectDeletion = false"></v-btn>
          <v-btn text="Delete" variant="tonal" @click="confirmProjectDeletion()"></v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!--Project deletion error dialog-->
    <v-dialog v-model="dialogProjectDeletionError" :max-width="variablesStore.errorMaxWidth">
      <v-card
        title="Error!"
        prepend-icon="mdi-alert-circle"
        color="error"
        :text="projectDeletionErrorMessage + '. Please try again.'"
      >
        <v-card-actions>
          <v-btn @click="dialogProjectDeletionError = false" text="Close"></v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

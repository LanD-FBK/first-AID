<script>
import dataService from '@/components/dataService.js'

export default {
  name: 'dialog-manage-docs',
  data() {
    return {
      files: undefined,
    }
  },
  props: {
    id: Number
  },
  emits: ['exit'],
  methods: {
    removeDocument: function (documentID) {
      const self = this
      dataService.deleteProjectFiles(this.id, documentID).then(function () {
        self.updateFiles()
      })
    },
    uploadDocs: function () {
      const self = this
      let files = document.getElementById('uploadFiles').files
      dataService
        .uploadFiles(this.id, files)
        .then(function () {
          self.updateFiles()
        })
        .catch(function (error) {
          console.log(error)
          //TODO: error handling with error dialog component
        })
    },
    updateFiles: function () {
      const self = this
      dataService.getProjectFiles(this.id).then(function (data) {
        self.files = data.data
      })
    }
  },
  mounted() {
    this.updateFiles()
  }
}
</script>

<template>
  <v-card prepend-icon="mdi-file-document-multiple-outline" title="Manage Project Documents">
    <v-card-text>
      <!--TODO: center spinner-->
      <v-progress-circular
        indeterminate
        class="mx-auto"
        v-if="files === undefined"
      ></v-progress-circular>
      <template v-else-if="files.length === 0">
        <v-row>
          <!--TODO: fix spacing-->
          <p class="text-caption text-medium-emphasis ma-3">There are no files in this project</p>
        </v-row>
        <v-row>
          <input type="file" multiple id="uploadFiles" class="ma-2" />
        </v-row>
      </template>
      <template v-else>
        <v-list>
          <v-list-item
            v-for="file of files"
            :key="file.id"
            :title="file.name"
            :subtitle="'File ID: ' + file.id"
          >
            <template v-slot:append>
              <!--TODO: add spinner after click to let user know that deletion is in progress-->
              <v-btn icon="mdi-delete" variant="flat" @click="removeDocument(file.id)" />
            </template>
          </v-list-item>
        </v-list>
        <input type="file" multiple id="uploadFiles" class="ma-2" />
      </template>
    </v-card-text>
    <v-card-actions>
      <v-btn color="primary" variant="outlined" @click="uploadDocs()">Upload</v-btn>
      <v-btn color="primary" variant="flat" @click="$emit('exit')">Done</v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped></style>
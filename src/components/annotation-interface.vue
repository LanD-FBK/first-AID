<script>
import dataService from './dataService';

export default {
  data(){
    return{
      temporaryID: 13,
      selectedFile: undefined,
      files: undefined,
      filesContent: [],
      dialog: [{
        name: 'Actor',
        dialog: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
      }]
    }
  },
  mounted: function(){
    const self = this
    //getProjectFiles(this.$route.params.projectID)
    dataService.getProjectFiles(this.temporaryID).then(function(data){
      self.files = data.data
    })
  },
  methods: {
    getSelectedTextOffset: function(){
      let start = window.getSelection().anchorOffset
      let finish = window.getSelection().focusOffset
      let item = document.getSelection()
      return String(start + ' ' + finish + '. Item: ' + this.selectedFile)
    },
    selectedItem: function(id){
      if(
        (Math.max(
        window.getSelection().anchorOffset, 
        window.getSelection().focusOffset
      ) - Math.min(
        window.getSelection().anchorOffset, 
        window.getSelection().focusOffset
      )) == 0){
        this.selectedFile = id
        console.log(this.selectedFile)
      }
    }
  },
  watch: {
    files(newValue, oldValue){
      const self = this
      if(oldValue == undefined){
        for(let file of newValue){
        dataService.getFileContent(this.temporaryID, file.id).then(function(data){
          self.filesContent.push({
            title: file.name,
            text: String(data.data),
            id: file.id
          })
    })
  }
      }
    }
  }
}
</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="4">
        <p class="text-h4 ma-2">Files</p>
        <v-expansion-panels ref="documentText" v-for="file of filesContent" :key="file.id">
  <v-expansion-panel class="ma-2" ref="documentDirect" :title="file.title" :text="file.text" @mouseenter="selectedItem(file.id)">
</v-expansion-panel>
</v-expansion-panels>
      </v-col>
      <v-divider vertical></v-divider>
      <v-col cols="4">
        <p class="text-h4 ma-2">Dialog</p>
        <v-row v-for="i in 3" :key="i">
          <v-col>
        <v-textarea :label="dialog[0].name" v-model="dialog[0].dialog">
          <template v-slot:append>
            <v-btn icon="mdi-link-variant-plus" variant="outline" class="mx-auto"/>
            <v-btn icon="mdi-trash-can-outline" variant="outline" class="mx-auto"/>
          </template>
        </v-textarea>
        <div class="d-flex justify-center">
        <v-btn icon="mdi-plus" :size="30"/>
      </div>
      </v-col>
      </v-row>
      </v-col>
      <v-divider vertical></v-divider>
      <v-col cols="4">
        <p class="text-h4 ma-2">Annotations</p>
        <v-card>
          <v-card-text>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec pharetra vestibulum ultrices. Fusce bibendum tempus porttitor. Duis faucibus congue felis eget ultrices.</v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

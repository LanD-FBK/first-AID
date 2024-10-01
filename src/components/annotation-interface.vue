<script>
import dataService from './dataService'
import highlightable from '@/components/highlight-table.vue'
import { nextTick } from 'vue'

export default {
  components: { highlightable },
  data() {
    return {
      projectID: 0,
      selectedRound: 0,
      selectedFile: 0,
      files: undefined,
      fileContent: undefined,
      loadingFile: false,
      loadingData: true,
      fileContentBuffer: {},
      actorsLabels: undefined,
      actors: undefined,
      annotation_data: undefined,
      toBeSelected: undefined,
      dialog: [{
        name: 'Actor',
        dialog: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
      }]
    }
  },
  mounted: function() {
    const self = this
    this.projectID = this.$route.params.projectID
    this.taskID = this.$route.params.taskID
    self.actorsLabels = {}
    self.files = {}
    self.actors = []
    self.annotation_data = {}

    dataService.getTaskInfo(this.projectID, this.taskID).then(function(data) {
      self.annotation_data = data.data?.meta?.new_annotation_data
      if (self.annotation_data === undefined || self.annotation_data.length === 0) {
        self.annotation_data = {}
      }
      for (let a of data.data.actors) {
        self.actorsLabels[a.label] = a.name
      }
      self.actors = data.data.actors
      for (let f of data.data.files) {
        self.files[f.file.id] = f.file
      }
    }).catch().then(function() {
      self.loadingData = false
    })
  },
  computed: {
    filesForSelect: function() {
      let newList = []
      newList.push({
        'title': '[Select file]',
        'value': 0
      })
      if (this.files) {
        for (let i in this.files) {
          newList.push({
            'title': this.files[i].name,
            'subtitle': this.files[i].size + ' bytes',
            'value': this.files[i].id
          })
        }
      }
      return newList
    },
    rolesForSelect: function() {
      let newList = []
      for (let i in this.actors) {
        newList.push({
          'title': this.actors[i].name,
          'value': this.actors[i].label
        })
      }
      return newList
    }
  },
  methods: {
    onLink: function(text, offset_start, offset_end) {
      let newGround = {
        'text': text,
        'file_id': this.selectedFile,
        'offset_start': Math.min(offset_start, offset_end),
        'offset_end': Math.max(offset_start, offset_end)
      }
      this.annotation_data[this.selectedRound].ground.push(newGround)
    },
    deleteRound: function(index) {
      this.annotation_data.splice(index, 1)
    },
    addRound: function(index) {
      let replaceIndex = index + 1
      let s = undefined
      let leave = false
      if (this.annotation_data.length > replaceIndex) {
        s = this.annotation_data[replaceIndex].speaker
      } else if (this.annotation_data.length > 0) {
        s = this.annotation_data[this.annotation_data.length - 1].speaker
        leave = true
      } else {
        // get the second one
        s = this.actors[1].label
      }
      let chosenActor = undefined
      if (leave) {
        chosenActor = s
      }
      else {
        let limit = 2
        let count = 0
        let previous = undefined
        while (chosenActor === undefined) {
          count++
          if (count > limit) {
            break
          }
          for (let a of this.actors) {
            if (a.label === s && previous !== undefined) {
              chosenActor = previous
              break
            }
            previous = a.label
          }
        }
      }

      if (!this.annotation_data) {
        this.annotation_data = []
      }
      if (this.annotation_data.length > 0) {
        this.annotation_data.splice(replaceIndex, 0, {
          "speaker": chosenActor, "text": "", ground: []
        })

      }
      else {
        this.annotation_data = []
        this.annotation_data.push({
          "speaker": chosenActor, "text": "", ground: []
        })

      }
    },
    deleteGround: function(index, gindex) {
      this.annotation_data[index].ground.splice(gindex, 1)
    },
    selectText: function(g) {
      this.selectedFile = g.file_id
      this.toBeSelected = g
      this.loadFile()
    },
    loadSelection: function() {
      let vueThis = this
      nextTick().then(function() {
        if (vueThis.toBeSelected !== undefined) {
          // https://stackoverflow.com/questions/17675056/set-selection-by-range-in-javascript
          // https://developer.mozilla.org/en-US/docs/Web/API/Range/setStart
          var selection = window.getSelection()
          var range = document.createRange()
          let referenceNode = document.getElementById('file-content').childNodes[0]
          range.setStart(referenceNode, vueThis.toBeSelected.offset_start)
          range.setEnd(referenceNode, vueThis.toBeSelected.offset_end)
          selection.removeAllRanges()
          selection.addRange(range)

          vueThis.toBeSelected = undefined
        }
      })

    },
    loadFile: function() {
      if (this.selectedFile) {
        if (this.selectedFile in this.fileContentBuffer) {
          this.fileContent = this.fileContentBuffer[this.selectedFile]
          this.loadSelection()
        } else {
          let vueThis = this
          this.loadingFile = true
          dataService.getFileContent(this.projectID, this.selectedFile).then(function(data) {
            vueThis.fileContentBuffer[vueThis.selectedFile] = data.data
            vueThis.fileContent = vueThis.fileContentBuffer[vueThis.selectedFile]
            vueThis.loadingFile = false
            vueThis.loadSelection()
          }).catch(function() {
            vueThis.loadingFile = false
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
      <v-col cols="4" id="pre-col">
        <p class="text-h4 ma-2">Files</p>
        <v-select :items="filesForSelect" :item-props="true" v-model="selectedFile"
                  @update:model-value="loadFile"></v-select>
        <highlightable v-if="selectedFile && !loadingFile"
                       @link="onLink"
        >
          <pre id="file-content">{{ fileContent }}</pre>
        </highlightable>
        <v-skeleton-loader type="paragraph" v-if="loadingFile"></v-skeleton-loader>
      </v-col>
      <v-divider vertical></v-divider>
      <v-col cols="8">
        <v-row>
          <v-col cols="6">
            <p class="text-h4 ma-2 text-center">Dialog</p>
            <div class="d-flex justify-center">
              <v-btn icon="mdi-plus" @click="addRound(-1)" />
            </div>
          </v-col>
          <v-divider vertical></v-divider>
          <v-col cols="6">
            <p class="text-h4 ma-2 text-center">Ground</p>
          </v-col>
        </v-row>
        <v-row v-for="(round, index) in annotation_data" :key="index"
               :class="{'selected-row': selectedRound === index}"
               @click="selectedRound = index">
          <v-col cols="6">
            <v-row>
              <v-col>
                <v-select :items="rolesForSelect" :item-props="true" v-model="round['speaker']"></v-select>
                <v-textarea v-model="round['text']" @focus="selectedRound = index">
                </v-textarea>
                <div class="d-flex justify-center">
                  <v-btn class="ma-1" icon="mdi-link-variant-plus" readonly="readonly"
                         :class="{'bg-deep-orange': selectedRound === index}" />
                  <v-btn class="ma-1" icon="mdi-trash-can-outline" @click="deleteRound(index)" />
                  <v-btn class="ma-1" icon="mdi-plus" @click="addRound(index)" />
                </div>
              </v-col>
            </v-row>
          </v-col>
          <v-divider vertical></v-divider>
          <v-col cols="6">
            <v-card v-if="round.ground.length > 0">
              <v-list class="ground-list">
                <v-list-item v-for="(g, gindex) in round.ground" :key="gindex" :title="files[g.file_id].name"
                             :subtitle="g.text" @click="selectText(g)">
                  <template v-slot:append>
                    <v-btn
                      color="red"
                      icon="mdi-trash-can-outline"
                      variant="text"
                      @click.stop="deleteGround(index, gindex)"
                    ></v-btn>
                  </template>
                </v-list-item>
              </v-list>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<style>

.selected-row {
  background-color: #eee;
  position: relative;
}

div.selected-row-label {
  position: absolute;
  bottom: 5px;
  left: 5px;
  font-weight: bold;
  background-color: brown;
  color: white;
  padding: 2px 5px;
}

.ground-list .v-list-item-title {
  font-size: .8em;
}

#file-content {
  white-space: pre-wrap; /* Since CSS 2.1 */
  word-wrap: break-word; /* Internet Explorer 5.5+ */

  /*  overflow-y: auto;
    height: 100%;
    flex-grow: 1;*/
}

/*#pre-col {
  display: flex;
  flex-direction: column;

}*/
</style>
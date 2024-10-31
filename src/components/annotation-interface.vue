<script>
import dataService from './dataService'
import highlightable from '@/components/highlight-table.vue'
import { nextTick } from 'vue'
import { Pane, Splitpanes } from 'splitpanes'

export default {
  components: { highlightable, Splitpanes, Pane },
  data() {
    return {
      annotationID: undefined,
      annotationParent: 0,
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
      comment: '',
      dialog: [
        {
          name: 'Actor',
          dialog: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
        }
      ]
    }
  },
  mounted: function () {
    const vueThis = this
    this.projectID = this.$route.params.projectID
    this.taskID = this.$route.params.taskID
    this.annotationID = this.$route.params.annotationID
    this.annotationParent = this.$route.params.annotationParent

    vueThis.actorsLabels = {}
    vueThis.files = {}
    vueThis.actors = []
    vueThis.annotation_data = {}

    let promises = []
    promises.push(dataService.getTaskInfo(this.projectID, this.taskID))
    if (this.annotationID) {
      promises.push(dataService.getAnnotation(this.projectID, this.taskID, this.annotationID))
    }
    else if (this.annotationParent) {
      promises.push(dataService.getAnnotation(this.projectID, this.taskID, this.annotationParent))
    }

    Promise.all(promises).then(function (result) {
      if (vueThis.annotationID || vueThis.annotationParent) {
        vueThis.annotation_data = result[1].data.annotations.data
        vueThis.comment = result[1].data.comment
      } else {
        vueThis.annotation_data = result[0].data?.meta?.new_annotation_data
        if (vueThis.annotation_data === undefined || vueThis.annotation_data.length === 0) {
          vueThis.annotation_data = {}
        }
      }
      console.log(vueThis.annotation_data)
      for (let a of result[0].data.actors) {
        vueThis.actorsLabels[a.label] = a.name
      }
      vueThis.actors = result[0].data.actors
      for (let f of result[0].data.files) {
        vueThis.files[f.file.id] = f.file
      }
      vueThis.loadingData = false
    })

    // dataService.getTaskInfo(this.projectID, this.taskID).then(function(data) {
    //   self.annotation_data = data.data?.meta?.new_annotation_data
    //   if (self.annotation_data === undefined || self.annotation_data.length === 0) {
    //     self.annotation_data = {}
    //   }
    //   for (let a of data.data.actors) {
    //     self.actorsLabels[a.label] = a.name
    //   }
    //   self.actors = data.data.actors
    //   for (let f of data.data.files) {
    //     self.files[f.file.id] = f.file
    //   }
    // }).catch().then(function() {
    //   self.loadingData = false
    // })
  },
  computed: {
    filesForSelect: function () {
      let newList = []
      newList.push({
        title: '[Select file]',
        value: 0
      })
      if (this.files) {
        for (let i in this.files) {
          newList.push({
            title: this.files[i].name,
            subtitle: this.files[i].size + ' bytes',
            value: this.files[i].id
          })
        }
      }
      return newList
    },
    rolesForSelect: function () {
      let newList = []
      for (let i in this.actors) {
        // use base-color
        newList.push({
          title: this.actors[i].name,
          value: this.actors[i].label
        })
      }
      return newList
    }
  },
  methods: {
    confirmAnnotation: function () {
      let annotation = { data: this.annotation_data }
      let vueThis = this

      if (this.annotationID) {
        dataService
          .editAnnotation(this.projectID, this.taskID, this.annotationID, annotation, this.comment)
          .then(function () {
            vueThis.$router.push({ name: 'tasks', params: { projectID: vueThis.projectID } })
          })
          .catch(function (error) {
            console.log(error)
          })
      }
      else {
        dataService
          .createAnnotation(this.projectID, this.taskID, annotation, this.comment, this.annotationParent)
          .then(function () {
            vueThis.$router.push({ name: 'tasks', params: { projectID: vueThis.projectID } })
          })
          .catch(function (error) {
            console.log(error)
          })
      }
    },
    cancel: function () {
      // this.$router.push({ name: 'projects' })
      this.$router.push({ name: 'tasks', params: { projectID: this.projectID } })
    },
    scrollToPos: function () {
      const selection = window.getSelection()
      let top = selection.getRangeAt(0).getBoundingClientRect().top
      let height = selection.getRangeAt(0).getBoundingClientRect().height
      let preOffset = document.getElementById('file-content').offsetTop
      let winHeight = window.innerHeight

      if (top < preOffset || top > winHeight - height) {
        let to = document.getElementById('high-file-content').scrollTop - (preOffset - top)
        document.getElementById('high-file-content').scrollTo({ top: to, behavior: 'smooth' })
      }
    },
    onLink: function (text, offset_start, offset_end) {
      let newGround = {
        text: text,
        file_id: this.selectedFile,
        offset_start: Math.min(offset_start, offset_end),
        offset_end: Math.max(offset_start, offset_end)
      }
      this.annotation_data[this.selectedRound].ground.push(newGround)
    },
    deleteRound: function (index) {
      this.annotation_data.splice(index, 1)
    },
    addRound: function (index) {
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
      } else {
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
          speaker: chosenActor,
          text: '',
          ground: []
        })
      } else {
        this.annotation_data = []
        this.annotation_data.push({
          speaker: chosenActor,
          text: '',
          ground: []
        })
      }
    },
    deleteGround: function (index, gindex) {
      this.annotation_data[index].ground.splice(gindex, 1)
    },
    selectText: function (g) {
      this.selectedFile = g.file_id
      this.toBeSelected = g
      this.loadFile()
    },
    loadSelection: function () {
      let vueThis = this
      nextTick().then(function () {
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
          vueThis.scrollToPos()

          vueThis.toBeSelected = undefined
        }
      })
    },
    loadFile: function () {
      if (this.selectedFile) {
        if (this.selectedFile in this.fileContentBuffer) {
          this.fileContent = this.fileContentBuffer[this.selectedFile]
          this.loadSelection()
        } else {
          let vueThis = this
          this.loadingFile = true
          dataService
            .getFileContent(this.projectID, this.selectedFile)
            .then(function (data) {
              vueThis.fileContentBuffer[vueThis.selectedFile] = data.data
              vueThis.fileContent = vueThis.fileContentBuffer[vueThis.selectedFile]
              vueThis.loadingFile = false
              vueThis.loadSelection()
            })
            .catch(function () {
              vueThis.loadingFile = false
            })
        }
      }
    }
  }
}
</script>

<template>
  <splitpanes class="default-theme">
    <pane min-size="20" class="file-pane" size="35">
      <p class="text-h4 ma-2">Files</p>
      <v-select
        :items="filesForSelect"
        :item-props="true"
        v-model="selectedFile"
        @update:model-value="loadFile"
      ></v-select>
      <highlightable v-if="selectedFile && !loadingFile" @link="onLink" id="high-file-content">
        <pre id="file-content">{{ fileContent }}</pre>
      </highlightable>
      <v-skeleton-loader id="file-loader" type="paragraph" v-if="loadingFile"></v-skeleton-loader>
      <div v-if="!selectedFile || loadingFile" class="empty-div">&nbsp;</div>
    </pane>
    <pane class="dialogue-pane">
      <v-container fluid id="dialogue-div" v-if="!loadingData">
        <v-row>
          <v-col cols="7" xl="8">
            <p class="text-h4 ma-2 text-center">Dialog</p>
          </v-col>
          <v-divider vertical></v-divider>
          <v-col cols="5" xl="4">
            <p class="text-h4 ma-2 text-center">Ground</p>
          </v-col>
        </v-row>
        <v-row
          v-for="(round, index) in annotation_data"
          :key="index"
          :class="{ 'selected-row': selectedRound === index }"
          @click="selectedRound = index"
        >
          <v-col cols="7" xl="8">
            <v-row>
              <v-col>
                <v-select :items="rolesForSelect" :item-props="true" v-model="round['speaker']">
                  <template #prepend>
                    <v-btn icon="" class="ma-1" @click="addRound(index - 1)">
                      <v-icon class="icon-up"></v-icon>
                    </v-btn>
                    <v-btn icon="" class="ma-1" @click="addRound(index)">
                      <v-icon class="icon-down"></v-icon>
                    </v-btn>
                  </template>
                  <template #append>
                    <v-btn
                      color="red"
                      class="ma-1"
                      icon="mdi-trash-can-outline"
                      @click="deleteRound(index)"
                    />
                  </template>
                </v-select>
                <v-textarea v-model="round['text']" @focus="selectedRound = index"></v-textarea>
              </v-col>
            </v-row>
          </v-col>
          <v-divider vertical></v-divider>
          <v-col cols="5" xl="4">
            <v-card v-if="round.ground.length > 0">
              <v-list class="ground-list">
                <v-list-item
                  v-for="(g, gindex) in round.ground"
                  :key="gindex"
                  :title="files[g.file_id].name"
                  :subtitle="g.text"
                  @click="selectText(g)"
                >
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
        <div class="bg-primary" id="buttons-container">
          <v-text-field label="Comment" bg-color="white" v-model="comment"></v-text-field>
          <v-btn prepend-icon="mdi-check" @click="confirmAnnotation">Confirm</v-btn>
          <v-btn prepend-icon="mdi-close" class="ms-3" @click="cancel">Cancel</v-btn>
        </div>
      </v-container>
    </pane>
  </splitpanes>
</template>

<style>
#buttons-container {
  position: sticky;
  bottom: 0;
  padding: 20px;
  text-align: right;
}

#buttons-container .v-btn {
  margin-left: 20px;
}

.icon-up {
  background-image: url('/plus_up.svg');
}

.icon-down {
  background-image: url('/plus_down.svg');
}

.selected-row {
  background-color: #fdd;
  position: relative;
}

/*
div.selected-row-label {
  position: absolute;
  bottom: 5px;
  left: 5px;
  font-weight: bold;
  background-color: brown;
  color: white;
  padding: 2px 5px;
}
*/

.ground-list .v-list-item-title {
  font-size: 0.8em;
}

#file-content {
  white-space: pre-wrap; /* Since CSS 2.1 */
  word-wrap: break-word; /* Internet Explorer 5.5+ */

  /*  overflow-y: auto;
    height: 100%;
    flex-grow: 1;*/
}

.file-pane {
  display: flex;
  flex-direction: column;
}

.empty-div {
  height: 100%;
}

#high-file-content {
  flex: 1 1 auto;
  overflow: auto;
  height: 100%;
}

.splitpanes__pane {
  padding: 10px;
}

#dialogue-div {
  overflow: auto;
  height: 100%;
  padding: 0;
}

/*#pre-col {
  display: flex;
  flex-direction: column;

}*/
</style>

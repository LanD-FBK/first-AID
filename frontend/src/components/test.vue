<template>
  <splitpanes class="default-theme">
    <pane min-size="20" class="file-pane">
      <p class="text-h4 ma-2">Files</p>
      <v-select :items="[]" :item-props="true"></v-select>
      <highlightable id="high-file-content">
        <pre id="file-content">{{ longText }}</pre>
      </highlightable>
    </pane>
    <pane>
      <v-btn @click="scrollToPos">Scroll</v-btn>
      <br />

      <div style="width:300px; height:300px; position:relative">
        <!-- This pre tag is used only for keeping the text as plain portion of text -->
        <pre class="userSelection" style="position:absolute;margin:0;top:0;color:rgba(0,0,0,0);">lorem ipsum, dolor sit amet consectetur adipisicing elit.Sint praesentium, ad repellat fuga consequuntur aut a laboriosam! Deserunt, fugiat aperiam, omnis esse vel, aliquid itaque in tempore sequi voluptatibus consequuntur.
            </pre>
        <!-- Using this tag you can style the elements-->
        <pre class="userSelection" style="margin:0;z-index:0;user-select: none;">lorem ipsum, dolor sit amet consectetur <span style="background-color:red; color: white;">adipisicing</span> elit.Sint praesentium, ad repellat fuga consequuntur aut a laboriosam! Deserunt, fugiat aperiam, omnis esse vel, aliquid itaque in tempore sequi voluptatibus consequuntur.
            </pre>

        <button onclick="handleClick()">Click here</button>
      </div>
    </pane>
  </splitpanes>
</template>

<script>
import { Splitpanes, Pane } from 'splitpanes'
import highlightable from '@/components/highlight-table.vue'

export default {
  data() {
    return {
      longText: `Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean luctus varius libero, at venenatis lorem volutpat ut. Suspendisse potenti.
      \nPraesent consequat ultrices erat, nec auctor tortor elementum in. Sed sit amet risus nec risus dignissim consequat ut id lorem.
      \nNam hendrerit massa libero, at convallis ante vehicula sed. Phasellus maximus pulvinar orci ut ultricies.
      \nNam nec justo lectus. Nullam sollicitudin, metus vitae dapibus vehicula, magna velit suscipit turpis, id bibendum sapien erat nec lectus.
      \nCras ac magna justo. Proin nec dui viverra, tincidunt nulla et, scelerisque odio.
      \n\nLorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean luctus varius libero, at venenatis lorem volutpat ut. Suspendisse potenti.
      \nPraesent consequat ultrices erat, nec auctor tortor elementum in. Sed sit amet risus nec risus dignissim consequat ut id lorem.
      \nNam hendrerit massa libero, at convallis ante vehicula sed. Phasellus maximus pulvinar orci ut ultricies.
      \nNam nec justo lectus. Nullam sollicitudin, metus vitae dapibus vehicula, magna velit suscipit turpis, id bibendum sapien erat nec lectus.
      \nCras ac magna justo. Proin nec dui viverra, tincidunt nulla et, scelerisque odio.`
    }
  },
  components: { highlightable, Splitpanes, Pane },
  methods: {
    scrollToPos: function() {
      const selection = window.getSelection()
      let top = selection.getRangeAt(0).getBoundingClientRect().top
      let height = selection.getRangeAt(0).getBoundingClientRect().height
      let preOffset = document.getElementById('file-content').offsetTop
      let winHeight = window.innerHeight

      if (top < preOffset || top > winHeight - height) {
        let to = document.getElementById('high-file-content').scrollTop - (preOffset - top)
        document.getElementById('high-file-content').scrollTo({ 'top': to, behavior: 'smooth' })
      }
    }
  }
}
</script>

<style>
.splitpanes__pane {
  padding: 10px;
}

.file-pane {
  display: flex;
  flex-direction: column;
}

#high-file-content {
  flex: 1 1 auto;
  overflow: auto;
  height: 100%;
}

.userSelection {
  white-space: pre-wrap; /* Since CSS 2.1 */
  word-wrap: break-word; /* Internet Explorer 5.5+ */
}

</style>

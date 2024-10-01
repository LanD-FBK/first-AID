<script>

// From here: https://codepen.io/tahazsh/pen/WYywXW

export default {
  data() {
    return {
      x: 0,
      y: 0,
      showTools: false,
      selectedText: '',
      startOffset: 0,
      endOffset: 0
    }
  },

  methods: {
    onMouseup() {
      const vueThis = this

      // This timeout allows the browser to get che right selection.
      // If removed, the icon is still visible when clicking on the highlighted text.
      setTimeout(function() {
        const selection = window.getSelection()

        // This is zero only after the timeout
        if (!selection.rangeCount) {
          vueThis.showTools = false
          return
        }

        const { x, y, width } = selection.getRangeAt(0).getBoundingClientRect()
        if (!width) {
          vueThis.showTools = false
          return
        }
        vueThis.x = x + (width / 2)
        vueThis.y = y + window.scrollY - 10
        vueThis.showTools = true
        vueThis.selectedText = selection.toString()
        if (vueThis.selectedText.length === 0) {
          vueThis.showTools = false
        }

        vueThis.startOffset = selection.anchorOffset
        vueThis.endOffset = selection.focusOffset
      }, 100)
    },

    handleAction() {
      this.showTools = false
      this.$emit('link', this.selectedText, this.startOffset, this.endOffset)
    }
  }

}
</script>

<template>
  <div>
    <div
      v-show="showTools"
      class="pre-tools"
      :style="{
        left: `${x}px`,
        top: `${y}px`
      }"
    >
      <span
        class="highlight-item"
        @click.prevent.stop="handleAction()"
      >
        <i class="mdi-link-variant-plus mdi v-icon notranslate v-theme--light v-icon--size-default"
           aria-hidden="true"></i>
      </span>
    </div>
    <div @mouseup="onMouseup">
      <slot />
    </div>
  </div>

</template>

<style>
.pre-tools {
  padding: 5px;
  background: #333;
  border-radius: 3px;
  position: absolute;
  top: 0;
  left: 0;
  transform: translate(-50%, -100%);
  transition: 0.2s all;
  display: flex;
  justify-content: center;
  align-items: center;
}

.pre-tools:after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: -5px;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid #333;
}

.pre-tools .highlight-item {
  color: #fff;
  cursor: pointer;
  display: block;
}

.pre-tools .highlight-item:hover {
  color: #19f;
}


</style>
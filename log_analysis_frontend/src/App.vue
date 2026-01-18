<script setup>
</script>

<template>
  <div id="app">
    <router-view />
  </div>
</template>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 16px;
  line-height: 1.5;
  color: #333;
  background-color: #f5f7fa;
}

/* 基础组件样式 */
#app {
  min-height: 100vh;
}

/* 按钮基础样式 */
button {
  cursor: pointer;
  font-family: inherit;
}

/* 表单元素基础样式 */
input, textarea, select {
  font-family: inherit;
  outline: none;
}

input:focus, textarea:focus, select:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

/* 标题样式 */
h1, h2, h3, h4, h5, h6 {
  color: #333;
  font-weight: 600;
}

/* 链接样式 */
a {
  color: #409eff;
  text-decoration: none;
}

a:hover {
  color: #66b1ff;
}
</style>

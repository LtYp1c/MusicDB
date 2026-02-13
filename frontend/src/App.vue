<template>
  <div id="app">
    <el-container>
      <el-header v-if="!isLoginRoute">
        <div class="header">
          <h1>🎵 音乐数据库</h1>
          <el-menu
            mode="horizontal"
            :default-active="activeIndex"
            :ellipsis="false"
            @select="handleSelect"
            class="menu"
          >
            <!-- 用户信息显示 -->
            <div class="user-info">
              <span class="username">{{ currentUsername }}</span>
              <span class="user-role" :class="{ 'admin-role': isAdmin }">{{ userRole }}</span>
            </div>
            
            <el-menu-item index="dashboard">首页</el-menu-item>
            <el-menu-item index="songs">歌曲列表</el-menu-item>
            <el-menu-item index="singers">歌手列表</el-menu-item>
            <el-menu-item index="albums">专辑列表</el-menu-item>
            <el-menu-item v-if="isAdmin" index="users">用户管理</el-menu-item>
            <el-menu-item index="favorites">收藏列表</el-menu-item>
            <el-menu-item index="playlists">播放列表</el-menu-item>
            <el-menu-item index="logout" style="margin-left: 20px;">退出登录</el-menu-item>
          </el-menu>
        </div>
      </el-header>
      
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { clearAuth, isAdmin as getIsAdmin, getUsername, isAuthed } from './utils/auth'

const route = useRoute()
const router = useRouter()

// 响应式数据
const activeIndex = ref('dashboard')

// 响应式权限状态
const authState = ref({
  isAdmin: getIsAdmin(),
  username: getUsername(),
  isAuthed: isAuthed()
})

// 监听路由变化
watch(() => route.name, (newRouteName) => {
  activeIndex.value = newRouteName || 'dashboard'
  
  // 路由变化时更新权限状态
  updateAuthState()
})

// 监听localStorage变化（用于跨标签页同步）
window.addEventListener('storage', (e) => {
  if (e.key === 'auth_role' || e.key === 'auth_username') {
    updateAuthState()
  }
})

// 监听权限状态变化事件（用于同一标签页内同步）
window.addEventListener('authStateChanged', () => {
  updateAuthState()
})

// 更新权限状态的方法
const updateAuthState = () => {
  authState.value = {
    isAdmin: getIsAdmin(),
    username: getUsername(),
    isAuthed: isAuthed()
  }
}

// 菜单选择处理
const handleSelect = (key) => {
  if (key === 'logout') {
    clearAuth()
    router.replace('/login')
    // 退出登录后立即更新权限状态
    updateAuthState()
    return
  }
  activeIndex.value = key
  router.push(`/${key}`)
}

// 计算属性
const isAdmin = computed(() => authState.value.isAdmin)
const isLoginRoute = computed(() => route.name === 'login')
const currentUsername = computed(() => authState.value.username || '用户')
const userRole = computed(() => authState.value.isAdmin ? '管理员' : '用户')
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.header h1 {
  margin: 0;
  color: #409EFF;
  font-size: 24px;
}

.menu {
  border-bottom: none;
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  margin-right: 20px;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.username {
  font-weight: 600;
  color: #303133;
  margin-right: 8px;
}

.user-role {
  padding: 2px 6px;
  background-color: #67c23a;
  color: white;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 500;
}

.user-role.admin-role {
  background-color: #f56c6c;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 20px;
}

.el-main {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 60px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    height: auto;
    padding: 10px 0;
  }
  
  .header h1 {
    margin-bottom: 10px;
    font-size: 20px;
  }
  
  .menu {
    flex-direction: column;
    width: 100%;
  }
  
  .user-info {
    margin-right: 0;
    margin-bottom: 10px;
    width: 100%;
    justify-content: center;
  }
}
</style>
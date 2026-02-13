<template>
  <div class="playlists-container">
    <div class="header">
      <h2>歌单管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建歌单
      </el-button>
    </div>

    <!-- 歌单列表 -->
    <div class="playlists-list">
      <el-row :gutter="20">
        <el-col :span="6" v-for="playlist in visiblePlaylists" :key="playlist.id" class="playlist-item">
          <el-card :body-style="{ padding: '0px' }">
            <div style="padding: 14px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h3 style="margin: 0;">{{ playlist.name }}</h3>
                <el-tag 
                  :type="playlist.is_public ? 'success' : 'info'" 
                  size="small"
                  effect="plain"
                >
                  {{ playlist.is_public ? '公开' : '私有' }}
                </el-tag>
              </div>
              <p class="description">{{ playlist.description || '暂无描述' }}</p>
              <div class="playlist-info">
                <span>创建者: {{ playlist.username || '未知用户' }}</span>
              </div>
              <div class="playlist-actions">
                <el-button text @click="viewPlaylist(playlist)">查看</el-button>
                <el-button text @click="editPlaylist(playlist)" v-if="isPlaylistOwner(playlist)">编辑</el-button>
                <el-button text type="danger" @click="deletePlaylist(playlist)" v-if="isPlaylistOwner(playlist)">删除</el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 创建歌单对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建歌单" width="500px">
      <el-form :model="newPlaylist" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="newPlaylist.name" placeholder="请输入歌单名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input 
            v-model="newPlaylist.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入歌单描述" 
          />
        </el-form-item>
        <el-form-item label="封面">
          <el-input v-model="newPlaylist.cover" placeholder="请输入封面图片URL" />
        </el-form-item>
        <el-form-item label="公开">
          <el-switch v-model="newPlaylist.is_public" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createPlaylist" :loading="loading">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑歌单对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑歌单" width="500px">
      <el-form :model="editingPlaylist" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="editingPlaylist.name" placeholder="请输入歌单名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input 
            v-model="editingPlaylist.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入歌单描述" 
          />
        </el-form-item>
        <el-form-item label="封面">
          <el-input v-model="editingPlaylist.cover" placeholder="请输入封面图片URL" />
        </el-form-item>
        <el-form-item label="公开">
          <el-switch v-model="editingPlaylist.is_public" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updatePlaylist" :loading="loading">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { playlistApi } from '@/api'
import { getUserId } from '@/utils/auth'

const router = useRouter()

const playlists = ref([])
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const loading = ref(false)
const currentUserId = ref(getUserId())

const newPlaylist = ref({
  name: '',
  description: '',
  cover: '',
  user_id: currentUserId.value, // 使用当前登录用户的ID
  is_public: false
})

const editingPlaylist = ref({})

// 判断当前用户是否为歌单创建者
const isPlaylistOwner = (playlist) => {
  return currentUserId.value && playlist.user_id === currentUserId.value
}

// 判断歌单是否对当前用户可见
const isPlaylistVisible = (playlist) => {
  // 如果歌单是公开的，所有用户都可以看到
  if (playlist.is_public) {
    return true
  }
  // 如果歌单是私有的，只有创建者可以看到
  return isPlaylistOwner(playlist)
}

// 获取对当前用户可见的歌单列表
const visiblePlaylists = computed(() => {
  return playlists.value.filter(playlist => isPlaylistVisible(playlist))
})

// 加载歌单
const loadPlaylists = async () => {
  try {
    console.log('开始加载歌单...')
    const response = await playlistApi.getPlaylists()
    console.log('API响应数据:', response)
    playlists.value = response
    console.log('歌单数据已设置:', playlists.value)
  } catch (error) {
    ElMessage.error('加载歌单失败')
    console.error('加载歌单失败:', error)
  }
}

// 创建歌单
const createPlaylist = async () => {
  if (!newPlaylist.value.name.trim()) {
    ElMessage.warning('请输入歌单名称')
    return
  }

  // 获取当前登录用户的ID
  const currentUserId = getUserId()
  if (!currentUserId) {
    ElMessage.error('请先登录')
    return
  }

  // 设置当前登录用户的ID
  const playlistData = {
    ...newPlaylist.value,
    user_id: currentUserId
  }

  loading.value = true
  try {
    await playlistApi.createPlaylist(playlistData)
    ElMessage.success('歌单创建成功')
    showCreateDialog.value = false
    resetNewPlaylist()
    loadPlaylists()
  } catch (error) {
    ElMessage.error('创建歌单失败')
    console.error('创建歌单失败:', error)
  } finally {
    loading.value = false
  }
}

// 编辑歌单
const editPlaylist = (playlist) => {
  // 权限验证：只有歌单创建者可以编辑
  if (!isPlaylistOwner(playlist)) {
    ElMessage.warning('您只能编辑自己创建的歌单')
    return
  }
  
  editingPlaylist.value = { ...playlist }
  showEditDialog.value = true
}

// 更新歌单
const updatePlaylist = async () => {
  if (!editingPlaylist.value.name.trim()) {
    ElMessage.warning('请输入歌单名称')
    return
  }

  // 权限验证：确保当前用户仍然是歌单创建者
  if (!isPlaylistOwner(editingPlaylist.value)) {
    ElMessage.warning('您只能编辑自己创建的歌单')
    return
  }

  loading.value = true
  try {
    await playlistApi.updatePlaylist(editingPlaylist.value.id, editingPlaylist.value)
    ElMessage.success('歌单更新成功')
    showEditDialog.value = false
    loadPlaylists()
  } catch (error) {
    ElMessage.error('更新歌单失败')
    console.error('更新歌单失败:', error)
  } finally {
    loading.value = false
  }
}

// 删除歌单
const deletePlaylist = async (playlist) => {
  // 权限验证：只有歌单创建者可以删除
  if (!isPlaylistOwner(playlist)) {
    ElMessage.warning('您只能删除自己创建的歌单')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除歌单"${playlist.name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await playlistApi.deletePlaylist(playlist.id)
    ElMessage.success('歌单删除成功')
    loadPlaylists()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除歌单失败')
      console.error('删除歌单失败:', error)
    }
  }
}

// 查看播放列表详情
const viewPlaylist = (playlist) => {
  // 跳转到播放列表详情页面
  router.push(`/playlists/${playlist.id}`)
}

// 重置新建播放列表表单
const resetNewPlaylist = () => {
  newPlaylist.value = {
    name: '',
    description: '',
    cover: '',
    user_id: 1, // 这里应该从登录用户信息中获取
    is_public: false
  }
}

onMounted(() => {
  loadPlaylists()
})
</script>

<style scoped>
.playlists-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.playlists-list {
  margin-top: 20px;
}

.playlist-item {
  margin-bottom: 20px;
}

.playlist-cover img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.description {
  color: #666;
  font-size: 14px;
  margin: 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.playlist-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
  margin: 8px 0;
}

.playlist-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}
</style>
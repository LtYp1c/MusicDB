<template>
  <div class="playlist-detail-container">
    <!-- 歌单头部信息 -->
    <div class="playlist-header">
      <div class="playlist-cover">
        <div class="default-cover">
          <el-icon><Headset /></el-icon>
          <span>暂无封面</span>
        </div>
      </div>
      
      <div class="playlist-info">
        <h1>{{ playlist.name }}</h1>
        <p class="description">{{ playlist.description || '暂无描述' }}</p>
        <div class="meta-info">
          <span class="creator">创建者: {{ playlist.username || '未知用户' }}</span>
          <el-tag :type="playlist.is_public ? 'success' : 'info'">
            {{ playlist.is_public ? '公开' : '私有' }}
          </el-tag>
          <span class="song-count">歌曲数量: {{ songs.length }}</span>
          <span class="create-time">创建时间: {{ formatDate(playlist.created_at) }}</span>
        </div>
        <div class="playlist-actions">
          <el-button @click="addSongsDialogVisible = true" v-if="isPlaylistOwner">
            <el-icon><Plus /></el-icon>
            添加歌曲
          </el-button>
          <el-button @click="editPlaylist" v-if="isPlaylistOwner">
            <el-icon><Edit /></el-icon>
            编辑歌单
          </el-button>
          <el-button @click="$router.back()">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
        </div>
      </div>
    </div>

    <!-- 歌曲列表 -->
    <el-card class="songs-card">
      <template #header>
        <div class="songs-header">
          <span>歌曲列表</span>
        </div>
      </template>

      <el-table
        :data="songs"
        v-loading="loading"
        stripe
        style="width: 100%"
        empty-text="歌单暂无歌曲"
      >
        <el-table-column type="index" width="60" label="#" />
        <el-table-column prop="name" label="歌曲名称" min-width="200" />
        <el-table-column prop="singer_name" label="歌手" min-width="120" />
        <el-table-column prop="album_name" label="专辑" min-width="150">
          <template #default="{ row }">
            {{ row.album_name || '未分类' }}
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="时长" width="100">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right" v-if="isPlaylistOwner">
          <template #default="{ row, $index }">
            <div class="action-buttons">
              <el-button size="small" type="danger" @click="removeSong(row, $index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加歌曲对话框 -->
    <el-dialog
      v-model="addSongsDialogVisible"
      title="添加歌曲到歌单"
      width="800px"
    >
      <div class="add-songs-dialog">
        <!-- 歌曲搜索和选择 -->
        <div class="search-section">
          <el-input
            v-model="songSearchKeyword"
            placeholder="搜索歌曲名称或歌手"
            clearable
            @input="handleSongSearch"
            style="width: 300px; margin-bottom: 20px;"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <!-- 歌曲列表 -->
        <el-table
          :data="filteredSongs"
          height="400"
          stripe
          style="width: 100%"
          empty-text="暂无歌曲数据"
          @selection-change="handleSelectionChange"
        >
          <el-table-column 
            type="selection" 
            width="55" 
            :selectable="isSongSelectable"
          />
          <el-table-column prop="name" label="歌曲名称" min-width="200" />
          <el-table-column prop="singer_name" label="歌手" min-width="120" />
          <el-table-column prop="album_name" label="专辑" min-width="150">
            <template #default="{ row }">
              {{ row.album_name || '未分类' }}
            </template>
          </el-table-column>
          <el-table-column prop="duration" label="时长" width="100">
            <template #default="{ row }">
              {{ formatDuration(row.duration) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <template #footer>
        <el-button @click="addSongsDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="addSelectedSongs"
          :disabled="selectedSongs.length === 0"
        >
          添加选中的歌曲 ({{ selectedSongs.length }}首)
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Headset, 
  Picture, 
  VideoPlay, 
  Plus, 
  ArrowLeft, 
  Search, 
  Delete,
  Edit
} from '@element-plus/icons-vue'
import { playlistApi, songApi } from '@/api'
import { getUserId } from '@/utils/auth'

const route = useRoute()
const router = useRouter()

const playlist = ref({})
const songs = ref([])
const allSongs = ref([])
const loading = ref(false)
const addSongsDialogVisible = ref(false)
const songSearchKeyword = ref('')
const selectedSongs = ref([])
const currentUserId = ref(getUserId())

// 获取歌单ID
const playlistId = computed(() => parseInt(route.params.id))

// 检查当前用户是否是歌单创建者
const isPlaylistOwner = computed(() => {
  return currentUserId.value && playlist.value.user_id === currentUserId.value
})

// 检查歌曲是否已经在歌单中
const isSongInPlaylist = (songId) => {
  return songs.value.some(song => song.id === songId)
}

// 过滤后的歌曲列表（用于添加歌曲对话框）
const filteredSongs = computed(() => {
  if (!songSearchKeyword.value) {
    return allSongs.value.filter(song => !isSongInPlaylist(song.id))
  }
  
  const keyword = songSearchKeyword.value.toLowerCase()
  return allSongs.value.filter(song => 
    !isSongInPlaylist(song.id) && (
      song.name.toLowerCase().includes(keyword) ||
      song.singer_name.toLowerCase().includes(keyword)
    )
  )
})

// 加载歌单详情
const loadPlaylistDetail = async () => {
  loading.value = true
  try {
    // 获取歌单基本信息
    playlist.value = await playlistApi.getPlaylist(playlistId.value)
    
    // 获取歌单中的歌曲
    const playlistSongs = await playlistApi.getPlaylistSongs(playlistId.value)
    
    // 获取歌曲详情信息
    if (playlistSongs.length > 0) {
      const songDetails = await Promise.all(
        playlistSongs.map(async (playlistSong) => {
          try {
            const song = await songApi.getSong(playlistSong.song_id)
            return {
              ...song,
              playlist_song_id: playlistSong.id // 保留播放列表歌曲关联ID
            }
          } catch (error) {
            console.error(`获取歌曲 ${playlistSong.song_id} 详情失败:`, error)
            return null
          }
        })
      )
      
      songs.value = songDetails.filter(song => song !== null)
    } else {
      songs.value = []
    }
  } catch (error) {
    ElMessage.error('加载歌单详情失败')
    console.error('加载歌单详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载所有歌曲（用于添加歌曲对话框）
const loadAllSongs = async () => {
  try {
    allSongs.value = await songApi.getSongs()
  } catch (error) {
    console.error('加载歌曲列表失败:', error)
  }
}



// 从歌单中移除歌曲
const removeSong = async (song, index) => {
  try {
    await ElMessageBox.confirm(
      `确定要从歌单中移除"${song.name}"吗？`,
      '确认移除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    try {
      // 调用API从歌单中移除歌曲
      await playlistApi.removeSongFromPlaylist(playlistId.value, song.id)
      
      // 从本地列表中移除歌曲
      songs.value.splice(index, 1)
      ElMessage.success('歌曲已从歌单中移除')
    } catch (error) {
      ElMessage.error('移除歌曲失败')
      console.error('移除歌曲失败:', error)
    }
  } catch (error) {
    // 用户取消操作
  }
}

// 处理歌曲搜索
const handleSongSearch = () => {
  // 搜索逻辑已经在computed属性中处理
}

// 检查歌曲是否可选择
const isSongSelectable = (row, index) => {
  return !isSongInPlaylist(row.id)
}

// 处理歌曲选择变化
const handleSelectionChange = (selection) => {
  selectedSongs.value = selection
}

// 添加选中的歌曲到歌单
const addSelectedSongs = async () => {
  if (selectedSongs.value.length === 0) {
    ElMessage.warning('请选择要添加的歌曲')
    return
  }

  try {
    // 添加歌曲到歌单
    for (const song of selectedSongs.value) {
      await playlistApi.addSongToPlaylist(playlistId.value, song.id)
    }
    
    ElMessage.success(`成功添加 ${selectedSongs.value.length} 首歌曲到歌单`)
    addSongsDialogVisible.value = false
    songSearchKeyword.value = ''
    selectedSongs.value = []
    
    // 重新加载歌单详情
    await loadPlaylistDetail()
  } catch (error) {
    ElMessage.error('添加歌曲失败')
    console.error('添加歌曲失败:', error)
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 编辑歌单
const editPlaylist = () => {
  ElMessage.info('编辑歌单功能暂未实现')
}

// 格式化时长
const formatDuration = (seconds) => {
  if (!seconds) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 生命周期
onMounted(() => {
  if (!playlistId.value) {
    ElMessage.error('歌单ID无效')
    router.back()
    return
  }
  
  loadPlaylistDetail()
  loadAllSongs()
})
</script>

<style scoped>
.playlist-detail-container {
  padding: 20px;
}

.playlist-header {
  display: flex;
  margin-bottom: 30px;
  background: #f8f9fa;
  padding: 30px;
  border-radius: 8px;
}

.playlist-cover {
  margin-right: 30px;
}

.default-cover {
  width: 200px;
  height: 200px;
  background: #e9ecef;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #6c757d;
}

.default-cover .el-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.image-error {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  color: #6c757d;
}

.playlist-info {
  flex: 1;
}

.playlist-info h1 {
  margin: 0 0 10px 0;
  font-size: 28px;
  color: #333;
}

.description {
  color: #666;
  margin-bottom: 20px;
  font-size: 16px;
  line-height: 1.5;
}

.meta-info {
  margin-bottom: 20px;
}

.meta-info span {
  margin-right: 20px;
  color: #666;
}

.playlist-actions {
  display: flex;
  gap: 10px;
}

.songs-card {
  margin-top: 20px;
}

.songs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

.add-songs-dialog {
  max-height: 500px;
  overflow-y: auto;
}

.search-section {
  margin-bottom: 20px;
}
</style>
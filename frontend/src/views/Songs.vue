<template>
  <div class="songs-container">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <h2>{{ isAdminComputed ? '歌曲管理' : '歌曲列表' }}</h2>
      <el-button v-if="isAdminComputed" type="primary" @click="handleAddSong">
        <el-icon><Plus /></el-icon>
        添加歌曲
      </el-button>
    </div>

    <!-- 搜索区域 -->
    <el-card class="search-card">
      <div class="search-filters">
        <el-input
          v-model="searchParams.keyword"
          placeholder="搜索歌曲名称或歌手"
          clearable
          @input="handleSearch"
          style="width: 300px;"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="searchParams.singerId"
          placeholder="选择歌手"
          clearable
          @change="handleSingerChange"
          style="width: 200px; margin-left: 10px;"
        >
          <el-option
            v-for="singer in singers"
            :key="singer.id"
            :label="singer.name"
            :value="singer.id"
          />
        </el-select>

        <el-select
          v-model="searchParams.albumId"
          placeholder="选择专辑"
          clearable
          @change="handleFilter"
          style="width: 200px; margin-left: 10px;"
          :disabled="!searchParams.singerId"
        >
          <el-option
            v-for="album in filteredAlbums"
            :key="album.id"
            :label="album.name"
            :value="album.id"
          />
        </el-select>

        <!-- 新增：流派筛选 -->
        <el-select
          v-model="searchParams.genreId"
          placeholder="选择流派"
          clearable
          @change="handleFilter"
          style="width: 200px; margin-left: 10px;"
        >
          <el-option
            v-for="genre in genres"
            :key="genre.id"
            :label="genre.name"
            :value="genre.id"
          />
        </el-select>
      </div>
    </el-card>

    <!-- 歌曲列表 -->
    <el-card>
      <el-table
        :data="filteredSongs"
        v-loading="loading"
        stripe
        style="width: 100%"
        empty-text="暂无歌曲数据"
      >
        <el-table-column prop="name" label="歌曲名称" min-width="200" />
        <el-table-column prop="singer_name" label="歌手" min-width="120" />
        <el-table-column prop="album_name" label="专辑" min-width="150">
          <template #default="{ row }">
            {{ row.album_name || '未分类' }}
          </template>
        </el-table-column>
        <!-- 新增：流派列 -->
        <el-table-column prop="genres" label="流派" min-width="150">
          <template #default="{ row }">
            <div class="genres-content">
              <template v-if="row.genres && row.genres.length > 0">
                <el-tag 
                  v-for="genre in row.genres" 
                  :key="genre"
                  type="info"
                  size="small"
                  style="margin-right: 5px; margin-bottom: 5px;"
                >
                  {{ genre }}
                </el-tag>
              </template>
              <span v-else style="color: #999;">暂无流派</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="时长" width="100">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button v-if="!isAdminComputed" size="small" @click="handleViewDetail(row)">
                 <el-icon><View /></el-icon>
                 查看详情
               </el-button>
               
              <el-button v-if="!isAdminComputed" size="small" :type="favoriteStatus[row.id] ? 'warning' : 'default'" @click="handleFavorite(row)">
                 <el-icon><StarFilled v-if="favoriteStatus[row.id]" /><Star v-else /></el-icon>
                 {{ favoriteStatus[row.id] ? '已收藏' : '收藏' }}
               </el-button>
               
              <el-button v-if="isAdminComputed" size="small" @click="handleEdit(row)">
                 <el-icon><Edit /></el-icon>
                 编辑
               </el-button>
               
               <el-button v-if="isAdminComputed" size="small" type="danger" @click="handleDelete(row)">
                 <el-icon><Delete /></el-icon>
                 删除
               </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 歌曲详情对话框 -->
    <el-dialog
      v-model="detailDialog.visible"
      :title="detailDialog.title"
      width="700px"
      :close-on-click-modal="false"
    >
      <div v-if="detailDialog.data" class="song-detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="歌曲名称">
            {{ detailDialog.data.name }}
          </el-descriptions-item>
          <el-descriptions-item label="歌手">
            {{ detailDialog.data.singer_name }}
          </el-descriptions-item>
          <el-descriptions-item label="专辑">
            {{ detailDialog.data.album_name || '未分类' }}
          </el-descriptions-item>
          <el-descriptions-item label="时长">
            {{ formatDuration(detailDialog.data.duration) }}
          </el-descriptions-item>
          <el-descriptions-item label="流派" :span="2">
            <div class="genres-content">
              <template v-if="detailDialog.data.genres && detailDialog.data.genres.length > 0">
                <el-tag 
                  v-for="genre in detailDialog.data.genres" 
                  :key="genre"
                  type="info"
                  style="margin-right: 5px; margin-bottom: 5px;"
                >
                  {{ genre }}
                </el-tag>
              </template>
              <span v-else style="color: #999;">暂无流派信息</span>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="歌词" :span="2">
            <div class="lyrics-content">
              {{ detailDialog.data.lyrics || '暂无歌词' }}
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <template #footer>
        <el-button @click="detailDialog.visible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 添加/编辑歌曲对话框 -->
    <el-dialog
      v-model="formDialog.visible"
      :title="formDialog.title"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="songFormRef"
        :model="formDialog.data"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="歌曲名称" prop="name">
          <el-input
            v-model="formDialog.data.name"
            placeholder="请输入歌曲名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="歌手" prop="singer_id">
          <el-select
            v-model="formDialog.data.singer_id"
            placeholder="请选择歌手"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="singer in singers"
              :key="singer.id"
              :label="singer.name"
              :value="singer.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="专辑">
          <el-select
            v-model="formDialog.data.album_id"
            placeholder="请选择专辑（可选）"
            style="width: 100%"
            clearable
            filterable
          >
            <el-option
              v-for="album in albums"
              :key="album.id"
              :label="album.name"
              :value="album.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="时长" prop="duration">
          <el-input-number
            v-model="formDialog.data.duration"
            :min="0"
            :max="3600"
            placeholder="请输入时长（秒）"
          />
          <span style="margin-left: 10px; color: #666;">秒</span>
        </el-form-item>
        
        <el-form-item label="流派">
          <el-select
            v-model="formDialog.data.genre_ids"
            placeholder="请选择流派（可多选）"
            style="width: 100%"
            multiple
            filterable
          >
            <el-option
              v-for="genre in genres"
              :key="genre.id"
              :label="genre.name"
              :value="genre.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="歌词">
          <el-input
            v-model="formDialog.data.lyrics"
            type="textarea"
            :rows="6"
            placeholder="请输入歌词"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="formDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="formDialog.loading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { songApi, singerApi, albumApi, favoriteApi, genreApi } from '../api'
import { isAdmin, getUserId } from '../utils/auth'
import { 
  View, 
  Plus, 
  Search, 
  Edit, 
  Delete,
  Star,
  StarFilled
} from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const songs = ref([])
const singers = ref([])
const albums = ref([])
const genres = ref([])
const songFormRef = ref()
const favoriteStatus = ref({}) // 存储歌曲收藏状态

// 搜索参数
const searchParams = reactive({
  keyword: '',
  singerId: null,
  albumId: null,
  genreId: null // 新增：流派筛选参数
})

// 分页配置
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 详情对话框
const detailDialog = reactive({
  visible: false,
  title: '歌曲详情',
  data: null
})

// 表单对话框
const formDialog = reactive({
  visible: false,
  title: '添加歌曲',
  loading: false,
  data: {
    name: '',
    singer_id: null,
    album_id: null,
    duration: null,
    lyrics: '',
    genre_ids: []
  }
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入歌曲名称', trigger: 'blur' },
    { min: 1, max: 100, message: '歌曲名称长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  singer_id: [
    { required: true, message: '请选择歌手', trigger: 'change' }
  ],
  duration: [
    { required: true, message: '请输入时长', trigger: 'blur' },
    { type: 'number', min: 0, max: 3600, message: '时长必须在 0 到 3600 秒之间', trigger: 'blur' }
  ]
}

// 计算属性
const isAdminComputed = computed(() => isAdmin())

// 过滤后的专辑列表（根据选中的歌手）
const filteredAlbums = computed(() => {
  if (!searchParams.singerId) {
    return albums.value
  }
  return albums.value.filter(album => album.singer_id === searchParams.singerId)
})

const filteredSongs = computed(() => {
  let filtered = songs.value
  
  // 关键词搜索
  if (searchParams.keyword) {
    const keyword = searchParams.keyword.toLowerCase()
    filtered = filtered.filter(song => 
      song.name.toLowerCase().includes(keyword) ||
      song.singer_name?.toLowerCase().includes(keyword)
    )
  }
  
  // 歌手筛选
  if (searchParams.singerId) {
    filtered = filtered.filter(song => song.singer_id === searchParams.singerId)
  }
  
  // 专辑筛选
  if (searchParams.albumId) {
    filtered = filtered.filter(song => song.album_id === searchParams.albumId)
  }
  
  // 新增：流派筛选
  if (searchParams.genreId) {
    // 预先获取选中的流派名称
    const selectedGenre = genres.value.find(g => g.id === searchParams.genreId)
    if (selectedGenre) {
      filtered = filtered.filter(song => 
        song.genres && song.genres.includes(selectedGenre.name)
      )
    }
  }
  
  // 分页处理
  pagination.total = filtered.length
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  
  return filtered.slice(start, end)
})

// 生命周期
onMounted(() => {
  loadData()
})

// 方法
const loadData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadSongs(),
      loadSingers(),
      loadAlbums(),
      loadGenres()
    ])
    
    // 如果是普通用户，加载收藏状态
    if (!isAdminComputed.value) {
      await loadFavoriteStatus()
    }
  } catch (error) {
    ElMessage.error('数据加载失败')
    console.error('数据加载失败:', error)
  } finally {
    loading.value = false
  }
}

const loadSongs = async () => {
  try {
    songs.value = await songApi.getSongs()
  } catch (error) {
    throw new Error('加载歌曲列表失败')
  }
}

const loadSingers = async () => {
  try {
    singers.value = await singerApi.getSingers()
  } catch (error) {
    console.error('加载歌手列表失败:', error)
  }
}

const loadAlbums = async () => {
  try {
    albums.value = await albumApi.getAlbums()
  } catch (error) {
    console.error('加载专辑列表失败:', error)
  }
}

const loadGenres = async () => {
  try {
    genres.value = await genreApi.getGenres()
  } catch (error) {
    console.error('加载流派列表失败:', error)
  }
}

// 加载用户收藏状态
const loadFavoriteStatus = async () => {
  try {
    const userId = getUserId()
    if (!userId) return
    
    const favorites = await favoriteApi.getUserFavorites(userId)
    
    // 初始化收藏状态
    favoriteStatus.value = {}
    favorites.forEach(favorite => {
      favoriteStatus.value[favorite.song_id] = true
    })
  } catch (error) {
    console.error('加载收藏状态失败:', error)
  }
}

// 处理收藏/取消收藏
const handleFavorite = async (song) => {
  try {
    const userId = getUserId()
    if (!userId) {
      ElMessage.error('请先登录')
      return
    }
    
    const isFavorited = favoriteStatus.value[song.id]
    
    if (isFavorited) {
      // 取消收藏
      await ElMessageBox.confirm(
        `确定要取消收藏"${song.name}"吗？`,
        '确认取消收藏',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      // 查找收藏记录ID
      const favorites = await favoriteApi.getUserFavorites(userId)
      const favorite = favorites.find(f => f.song_id === song.id)
      
      if (favorite) {
        await favoriteApi.deleteFavorite(favorite.id)
        ElMessage.success('取消收藏成功')
        favoriteStatus.value[song.id] = false
      }
    } else {
      // 添加收藏
      await favoriteApi.createFavorite({
        user_id: userId,
        song_id: song.id
      })
      ElMessage.success('收藏成功')
      favoriteStatus.value[song.id] = true
    }
  } catch (error) {
    if (error === 'cancel') {
      return
    }
    if (error.response?.data?.error === '已收藏该歌曲') {
      ElMessage.error('该歌曲已收藏')
      favoriteStatus.value[song.id] = true
    } else {
      // 重新获取当前状态以确定错误类型
      const currentFavorited = favoriteStatus.value[song.id]
      ElMessage.error(currentFavorited ? '取消收藏失败' : '收藏失败')
      console.error('收藏操作失败:', error)
    }
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
}

const handleFilter = () => {
  pagination.currentPage = 1
}

// 歌手选择事件
const handleSingerChange = () => {
  // 重置专辑选择
  searchParams.albumId = null
  pagination.currentPage = 1
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
}

const handleViewDetail = (song) => {
  detailDialog.data = { ...song }
  detailDialog.visible = true
}

const handleAddSong = () => {
  formDialog.title = '添加歌曲'
  formDialog.data = {
    name: '',
    singer_id: null,
    album_id: null,
    duration: null,
    lyrics: '',
    genre_ids: []
  }
  formDialog.visible = true
  
  // 清除表单验证
  nextTick(() => {
    songFormRef.value?.clearValidate()
  })
}

const handleEdit = async (song) => {
  formDialog.title = '编辑歌曲'
  formDialog.data = { ...song }
  
  // 加载歌曲的流派信息
  try {
    const songGenres = await genreApi.getSongGenres(song.id)
    formDialog.data.genre_ids = songGenres.map(sg => sg.genre_id)
  } catch (error) {
    console.error('加载歌曲流派信息失败:', error)
    formDialog.data.genre_ids = []
  }
  
  formDialog.visible = true
  
  // 清除表单验证
  nextTick(() => {
    songFormRef.value?.clearValidate()
  })
}

const handleSave = async () => {
  try {
    // 表单验证
    await songFormRef.value.validate()
    
    formDialog.loading = true
    
    const isEdit = formDialog.title === '编辑歌曲'
    
    if (isEdit) {
      await songApi.updateSong(formDialog.data.id, formDialog.data)
      ElMessage.success('歌曲更新成功')
    } else {
      await songApi.createSong(formDialog.data)
      ElMessage.success('歌曲添加成功')
    }
    
    formDialog.visible = false
    await loadSongs() // 重新加载歌曲数据
  } catch (error) {
    if (error && error.errors) {
      // 表单验证错误，不显示错误消息
      return
    }
    ElMessage.error(formDialog.title === '编辑歌曲' ? '更新失败' : '添加失败')
    console.error('保存失败:', error)
  } finally {
    formDialog.loading = false
  }
}

const handleDelete = async (song) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除歌曲"${song.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    await songApi.deleteSong(song.id)
    ElMessage.success('删除成功')
    await loadSongs() // 重新加载歌曲数据
  } catch (error) {
    if (error === 'cancel') {
      return
    }
    ElMessage.error('删除失败')
    console.error('删除失败:', error)
  }
}

const formatDuration = (seconds) => {
  if (!seconds) return '00:00'
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
}

// 导入 nextTick
import { nextTick } from 'vue'
</script>

<style scoped>
.songs-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
  font-weight: 600;
}

.search-card {
  margin-bottom: 20px;
}

.search-filters {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 流派标签样式 */
.genres-content {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.song-detail-content {
  line-height: 1.6;
}

.lyrics-content {
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  line-height: 1.8;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .songs-container {
    padding: 10px;
  }
  
  .search-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-filters .el-input,
  .search-filters .el-select {
    width: 100% !important;
    margin-left: 0 !important;
  }
  
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .page-header h2 {
    text-align: center;
  }
}
</style>
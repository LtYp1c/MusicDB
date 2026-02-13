<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon users">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.users }}</div>
              <div class="stat-label">用户总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon singers">
              <el-icon><Microphone /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.singers }}</div>
              <div class="stat-label">歌手总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon albums">
              <el-icon><Folder /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.albums }}</div>
              <div class="stat-label">专辑总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon songs">
              <el-icon><Headset /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.songs }}</div>
              <div class="stat-label">歌曲总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <div class="charts-section">
      <el-row :gutter="20">
        <!-- 热门歌手排行榜 -->
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <span>热门歌手排行榜</span>
            </template>
            <v-chart :option="topSingersOption" style="height: 300px;" />
          </el-card>
        </el-col>
        
        <!-- 用户活跃度统计 -->
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <span>用户活跃度统计</span>
            </template>
            <v-chart :option="userActivityOption" style="height: 300px;" />
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <!-- 热门歌曲排行榜 -->
        <el-col :span="24">
          <el-card class="chart-card">
            <template #header>
              <span>热门歌曲排行榜</span>
            </template>
            <v-chart :option="topSongsOption" style="height: 400px;" />
          </el-card>
        </el-col>
      </el-row>
    </div>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="7">
        <el-card>
          <template #header>
            <span>最新歌曲</span>
          </template>
          <el-table :data="recentSongs" style="width: 100%" size="small">
            <el-table-column prop="name" label="歌曲名称" min-width="100" />
            <el-table-column prop="singer_name" label="歌手" min-width="80" />
            <el-table-column prop="created_at" label="添加时间" width="100" align="center">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="7">
        <el-card>
          <template #header>
            <span>热门歌手</span>
          </template>
          <el-table :data="popularSingers" style="width: 100%" size="small">
            <el-table-column prop="name" label="歌手名称" min-width="120" />
            <el-table-column prop="favorite_count" label="收藏次数" width="80" align="center">
              <template #default="scope">
                <el-tag type="success" size="small">{{ scope.row.favorite_count }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="10">
        <el-card>
          <template #header>
            <span>个人推荐</span>
          </template>
          <el-table :data="recommendedSongs" style="width: 100%" size="small">
            <el-table-column prop="name" label="歌曲名称" min-width="120" />
            <el-table-column prop="singer_name" label="歌手" min-width="100" />
            <el-table-column label="流派" min-width="140">
              <template #default="{ row }">
                <div v-if="row.genres && row.genres.length > 0" class="genres-content">
                  <el-tag
                    v-for="genre in row.genres.slice(0, 2)"
                    :key="genre"
                    size="small"
                    type="info"
                    style="margin-right: 2px; margin-bottom: 1px;"
                  >
                    {{ genre }}
                  </el-tag>
                  <el-tag v-if="row.genres.length > 2" size="small" type="info">
                    +{{ row.genres.length - 2 }}
                  </el-tag>
                </div>
                <span v-else class="no-genre">暂无流派</span>
              </template>
            </el-table-column>
            <el-table-column prop="favorite_count" label="收藏次数" width="80" align="center">
              <template #default="{ row }">
                {{ row.favorite_count || 0 }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { userApi, singerApi, albumApi, songApi, statsApi, recommendationApi } from '../api'
import { User, Microphone, Folder, Headset } from '@element-plus/icons-vue'
import { getUserId } from '../utils/auth'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

export default {
  name: 'Dashboard',
  components: {
    User,
    Microphone,
    Folder,
    Headset,
    VChart
  },
  data() {
    return {
      stats: {
        users: 0,
        singers: 0,
        albums: 0,
        songs: 0
      },
      recentSongs: [],
      popularSingers: [],
      recommendedSongs: [],
      // 图表数据
      topSingersData: [],
      topSongsData: [],
      userActivityData: [],
      // 图表配置
      topSingersOption: {},
      topSongsOption: {},
      userActivityOption: {}
    }
  },
  mounted() {
    this.loadStats()
    this.loadRecentSongs()
    this.loadPopularSingers()
    this.loadRecommendations()
    this.loadChartsData()
  },
  methods: {
    async loadStats() {
      try {
        const [users, singers, albums, songs] = await Promise.all([
          userApi.getUsers(),
          singerApi.getSingers(),
          albumApi.getAlbums(),
          songApi.getSongs()
        ])
        
        this.stats = {
          users: users.length,
          singers: singers.length,
          albums: albums.length,
          songs: songs.length
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    },
    
    async loadRecentSongs() {
      try {
        const songs = await songApi.getSongs()
        this.recentSongs = songs.slice(-5).reverse()
      } catch (error) {
        console.error('加载最新歌曲失败:', error)
      }
    },
    
    async loadPopularSingers() {
      try {
        const popularSingers = await statsApi.getPopularSingers()
        this.popularSingers = popularSingers
      } catch (error) {
        console.error('加载热门歌手失败:', error)
        // 如果新API失败，回退到原来的方法
        try {
          const singers = await singerApi.getSingers()
          this.popularSingers = singers.slice(0, 5).map(singer => ({
            ...singer,
            favorite_count: 0
          }))
        } catch (fallbackError) {
          console.error('回退方法也失败:', fallbackError)
        }
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('zh-CN')
    },
    
    async loadRecommendations() {
      try {
        const userId = getUserId()
        if (userId) {
          // 获取个人推荐
          this.recommendedSongs = await recommendationApi.getRecommendations(userId)
        } else {
          // 如果没有登录用户，获取热门推荐
          this.recommendedSongs = await recommendationApi.getPopularRecommendations()
        }
      } catch (error) {
        console.error('加载推荐歌曲失败:', error)
        // 如果推荐API失败，显示空列表
        this.recommendedSongs = []
      }
    },

    // 加载图表数据
    async loadChartsData() {
      try {
        // 加载热门歌手图表数据
        const singersRes = await statsApi.getTopSingers()
        this.topSingersData = singersRes || []
        this.updateTopSingersChart()

        // 加载热门歌曲图表数据
        const songsRes = await statsApi.getTopSongs()
        this.topSongsData = songsRes || []
        this.updateTopSongsChart()

        // 加载用户活跃度图表数据
        const activityRes = await statsApi.getUserActivity()
        this.userActivityData = activityRes || []
        this.updateUserActivityChart()

      } catch (error) {
        console.error('加载图表数据失败:', error)
      }
    },

    // 更新热门歌手图表
    updateTopSingersChart() {
      const data = this.topSingersData || []
      this.topSingersOption = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: function(params) {
            const item = params[0]
            return `${item.name}<br/>收藏次数: ${item.value}`
          }
        },
        xAxis: {
          type: 'category',
          data: data.map(item => item.name || '未知歌手'),
          axisLabel: {
            rotate: 45
          }
        },
        yAxis: {
          type: 'value',
          name: '收藏次数'
        },
        series: [{
          data: data.map(item => item.favorite_count || 0),
          type: 'bar',
          itemStyle: {
            color: '#409EFF'
          }
        }]
      }
    },

    // 更新热门歌曲图表
    updateTopSongsChart() {
      const data = this.topSongsData || []
      this.topSongsOption = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: function(params) {
            const item = params[0]
            const song = data[item.dataIndex]
            return `${song.name || '未知歌曲'}<br/>歌手: ${song.singer_name || '未知歌手'}<br/>收藏次数: ${item.value}`
          }
        },
        xAxis: {
          type: 'category',
          data: data.map(item => item.name || '未知歌曲'),
          axisLabel: {
            rotate: 45
          }
        },
        yAxis: {
          type: 'value',
          name: '收藏次数'
        },
        series: [{
          data: data.map(item => item.favorite_count || 0),
          type: 'bar',
          itemStyle: {
            color: '#67C23A'
          }
        }]
      }
    },

    // 更新用户活跃度图表
    updateUserActivityChart() {
      const data = this.userActivityData || []
      this.userActivityOption = {
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            const item = params[0]
            const activity = data[item.dataIndex]
            return `日期: ${activity.date}<br/>收藏数量: ${item.value}`
          }
        },
        xAxis: {
          type: 'category',
          data: data.map(item => {
            const date = new Date(item.date)
            return `${date.getMonth() + 1}/${date.getDate()}`
          })
        },
        yAxis: {
          type: 'value',
          name: '收藏数量'
        },
        series: [{
          data: data.map(item => item.favorites || 0),
          type: 'line',
          smooth: true,
          itemStyle: {
            color: '#E6A23C'
          }
        }]
      }
    }
  }
}
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
  color: white;
}

.stat-icon.users {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.singers {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.albums {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.songs {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.charts-section {
  margin-top: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.no-genre {
  color: #909399;
  font-size: 12px;
}

.genres-content {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
}
</style>
/**
 * Pinia Store - 공과 상태 관리
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '../api'

export const useCurriculumStore = defineStore('curriculum', () => {
  // 상태
  const weeks = ref([])
  const currentWeekIndex = ref(0)
  const selectedWeekIndex = ref(0)
  const targetAudience = ref('성인')
  const targetAudiences = ref(['성인', '신회원', '청소년', '초등회'])
  
  const lessonData = ref(null)
  const generatedMaterial = ref('')
  const isGenerating = ref(false)
  const isCachedMaterial = ref(false)
  
  const qaList = ref([])
  const chatHistory = ref([])
  const isChatLoading = ref(false)
  
  const isLoading = ref(true)
  const error = ref(null)

  // Getters
  const selectedWeek = computed(() => weeks.value[selectedWeekIndex.value] || null)
  const weekRange = computed(() => selectedWeek.value?.week_range || '')

  // Actions
  async function loadInitialData() {
    isLoading.value = true
    error.value = null
    
    try {
      // 주차 목록과 현재 주차 정보 동시 로드
      const [weeksData, currentWeekData] = await Promise.all([
        api.getAvailableWeeks(),
        api.getCurrentWeek()
      ])
      
      weeks.value = weeksData
      currentWeekIndex.value = currentWeekData.index
      selectedWeekIndex.value = currentWeekData.index
      
      // 현재 주차의 공과 정보 로드
      if (selectedWeek.value) {
        await loadLessonData()
      }
    } catch (err) {
      error.value = '데이터를 불러오는 중 오류가 발생했습니다: ' + err.message
      console.error('Error loading initial data:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function loadLessonData() {
    if (!selectedWeek.value) return
    
    try {
      lessonData.value = await api.getCurriculumByWeek({
        start_date: selectedWeek.value.start_date,
        end_date: selectedWeek.value.end_date,
        week_range: selectedWeek.value.week_range
      })
      
      // Q&A 목록도 로드
      await loadQAList()
    } catch (err) {
      console.error('Error loading lesson data:', err)
      error.value = '공과 정보를 불러오는 중 오류가 발생했습니다.'
    }
  }

  async function selectWeek(index) {
    if (index === selectedWeekIndex.value) return
    
    // 주차 변경 시 기존 자료 초기화
    generatedMaterial.value = ''
    chatHistory.value = []
    isCachedMaterial.value = false
    
    selectedWeekIndex.value = index
    await loadLessonData()
  }

  function setTargetAudience(audience) {
    if (audience === targetAudience.value) return
    
    // 대상 변경 시 기존 자료 초기화
    generatedMaterial.value = ''
    chatHistory.value = []
    isCachedMaterial.value = false
    
    targetAudience.value = audience
    loadQAList()
  }

  async function generateMaterial() {
    if (!lessonData.value || isGenerating.value) return
    
    isGenerating.value = true
    error.value = null
    
    try {
      const result = await api.generateMaterial({
        lesson_title: lessonData.value.title,
        lesson_content: lessonData.value.content,
        target_audience: targetAudience.value,
        week_range: weekRange.value
      })
      
      generatedMaterial.value = result.material
      isCachedMaterial.value = result.is_cached
    } catch (err) {
      error.value = '공과 자료 생성 중 오류가 발생했습니다: ' + err.message
      console.error('Error generating material:', err)
    } finally {
      isGenerating.value = false
    }
  }

  async function sendChatMessage(question) {
    if (!lessonData.value || !generatedMaterial.value || isChatLoading.value) return
    
    isChatLoading.value = true
    
    // 사용자 메시지 추가
    chatHistory.value.push({
      role: 'user',
      content: question
    })
    
    try {
      const result = await api.sendChatMessage({
        lesson_title: lessonData.value.title,
        lesson_content: lessonData.value.content,
        reference_material: generatedMaterial.value,
        user_question: question,
        week_range: weekRange.value,
        target_audience: targetAudience.value
      })
      
      // AI 응답 추가
      chatHistory.value.push({
        role: 'assistant',
        content: result.answer
      })
      
      // Q&A 목록 새로고침
      await loadQAList()
      
    } catch (err) {
      chatHistory.value.push({
        role: 'assistant',
        content: '답변 생성 중 오류가 발생했습니다. 다시 시도해주세요.'
      })
      console.error('Error sending chat message:', err)
    } finally {
      isChatLoading.value = false
    }
  }

  async function loadQAList() {
    if (!weekRange.value) return
    
    try {
      qaList.value = await api.getQAList(weekRange.value, targetAudience.value)
    } catch (err) {
      console.error('Error loading QA list:', err)
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    // 상태
    weeks,
    currentWeekIndex,
    selectedWeekIndex,
    targetAudience,
    targetAudiences,
    lessonData,
    generatedMaterial,
    isGenerating,
    isCachedMaterial,
    qaList,
    chatHistory,
    isChatLoading,
    isLoading,
    error,
    
    // Getters
    selectedWeek,
    weekRange,
    
    // Actions
    loadInitialData,
    loadLessonData,
    selectWeek,
    setTargetAudience,
    generateMaterial,
    sendChatMessage,
    loadQAList,
    clearError
  }
})

/**
 * API 클라이언트
 * FastAPI 백엔드와 통신하는 함수들
 */

import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2분 타임아웃 (AI 생성에 시간이 걸릴 수 있음)
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 사용 가능한 주차 목록 가져오기
 */
export async function getAvailableWeeks() {
  const response = await api.get('/weeks')
  return response.data
}

/**
 * 현재 주차 정보 가져오기
 */
export async function getCurrentWeek() {
  const response = await api.get('/weeks/current')
  return response.data
}

/**
 * 특정 주차의 공과 정보 가져오기
 */
export async function getCurriculumByWeek(weekData) {
  const response = await api.post('/curriculum', weekData)
  return response.data
}

/**
 * 공과 자료 생성
 */
export async function generateMaterial(data) {
  const response = await api.post('/generate-material', data)
  return response.data
}

/**
 * 채팅 응답 생성
 */
export async function sendChatMessage(data) {
  const response = await api.post('/chat', data)
  return response.data
}

/**
 * Q&A 목록 가져오기
 */
export async function getQAList(weekRange, targetAudience) {
  const encodedWeekRange = encodeURIComponent(weekRange)
  const encodedAudience = encodeURIComponent(targetAudience)
  const response = await api.get(`/qa/${encodedWeekRange}/${encodedAudience}`)
  return response.data
}

/**
 * 대상 그룹 목록 가져오기
 */
export async function getTargetAudiences() {
  const response = await api.get('/target-audiences')
  return response.data
}

export default api

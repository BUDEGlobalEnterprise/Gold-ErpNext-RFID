import { ref, onMounted, onUnmounted } from 'vue'

/**
 * useDraggable — Composable for making elements draggable
 * 
 * @param {Object} options 
 * @param {string} options.storageKeyX - Key for localStorage persistence (X)
 * @param {string} options.storageKeyY - Key for localStorage persistence (Y)
 * @param {Object} options.initialPos - { x, y } initial position
 * @param {number} options.margin - Margin from screen edges
 * @param {number} options.size - Size of the draggable element (for constraints)
 */
export function useDraggable(options = {}) {
  const {
    storageKeyX = null,
    storageKeyY = null,
    initialPos = { x: window.innerWidth - 80, y: window.innerHeight - 80 },
    margin = 16,
    size = 56
  } = options

  const position = ref({
    x: storageKeyX && localStorage.getItem(storageKeyX) 
      ? parseInt(localStorage.getItem(storageKeyX)) 
      : initialPos.x,
    y: storageKeyY && localStorage.getItem(storageKeyY) 
      ? parseInt(localStorage.getItem(storageKeyY)) 
      : initialPos.y
  })

  const isDragging = ref(false)
  const dragOffset = ref({ x: 0, y: 0 })
  const hasMoved = ref(false)

  function startDrag(e) {
    isDragging.value = true
    hasMoved.value = false
    
    const clientX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX
    const clientY = e.type === 'touchstart' ? e.touches[0].clientY : e.clientY
    
    dragOffset.value = {
      x: clientX - position.value.x,
      y: clientY - position.value.y
    }
    
    window.addEventListener('mousemove', handleDrag)
    window.addEventListener('touchmove', handleDrag, { passive: false })
    window.addEventListener('mouseup', stopDrag)
    window.addEventListener('touchend', stopDrag)
  }

  function handleDrag(e) {
    if (!isDragging.value) return
    
    if (e.type === 'touchmove') e.preventDefault()
    
    const clientX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX
    const clientY = e.type === 'touchmove' ? e.touches[0].clientY : e.clientY
    
    const dx = clientX - (position.value.x + dragOffset.value.x)
    const dy = clientY - (position.value.y + dragOffset.value.y)
    
    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
      hasMoved.value = true
    }

    let newX = clientX - dragOffset.value.x
    let newY = clientY - dragOffset.value.y
    
    // Constrain to screen
    newX = Math.max(margin, Math.min(newX, window.innerWidth - size - margin))
    newY = Math.max(margin, Math.min(newY, window.innerHeight - size - margin))
    
    position.value = { x: newX, y: newY }
  }

  function stopDrag() {
    if (isDragging.value) {
      isDragging.value = false
      if (storageKeyX) localStorage.setItem(storageKeyX, position.value.x)
      if (storageKeyY) localStorage.setItem(storageKeyY, position.value.y)
    }
    
    window.removeEventListener('mousemove', handleDrag)
    window.removeEventListener('touchmove', handleDrag)
    window.removeEventListener('mouseup', stopDrag)
    window.removeEventListener('touchend', stopDrag)
  }

  function checkConstraints() {
    if (position.value.x > window.innerWidth - size - margin) {
      position.value.x = window.innerWidth - size - margin
    }
    if (position.value.y > window.innerHeight - size - margin) {
      position.value.y = window.innerHeight - size - margin
    }
  }

  onMounted(() => {
    checkConstraints()
    window.addEventListener('resize', checkConstraints)
  })

  onUnmounted(() => {
    stopDrag()
    window.removeEventListener('resize', checkConstraints)
  })

  return {
    position,
    isDragging,
    hasMoved,
    startDrag,
    stopDrag
  }
}

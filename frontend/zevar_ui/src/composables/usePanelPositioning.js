/**
 * Panel Positioning Composable
 * 
 * Handles the calculation of panel coordinates relative to the FAB
 * and ensures it stays within screen boundaries.
 */
import { computed } from 'vue'

export function usePanelPositioning(panelPosition, fabPosition, isPanelDragging) {
  const panelStyle = computed(() => {
    const isInitial = panelPosition.value.x === -1
    
    if (isInitial) {
      return {
        visibility: 'hidden',
        opacity: 0,
        pointerEvents: 'none'
      }
    }

    return {
      left: `${panelPosition.value.x}px`,
      top: `${panelPosition.value.y}px`,
      bottom: 'auto',
      right: 'auto',
      cursor: isPanelDragging.value ? 'grabbing' : 'default'
    }
  })

  function getFabRelativePosition() {
    const fabSize = 56
    const panelWidth = 400
    const panelMaxHeight = 600
    const margin = 16
    
    let x = fabPosition.value.x + fabSize / 2 - panelWidth / 2
    let y = fabPosition.value.y - panelMaxHeight - 12
    
    // Boundary checks
    x = Math.max(margin, Math.min(x, window.innerWidth - panelWidth - margin))
    if (y < margin) y = fabPosition.value.y + fabSize + 12
    y = Math.min(y, window.innerHeight - 200)

    return { x, y }
  }

  function initializePosition() {
    if (panelPosition.value.x === -1) {
      panelPosition.value = getFabRelativePosition()
    }
  }

  return {
    panelStyle,
    getFabRelativePosition,
    initializePosition
  }
}

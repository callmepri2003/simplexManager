
import styled from 'styled-components'

export default function SpacedComponent({children}){
  const SpacedComponentObj = styled.div`
    margin: 10px
  `
  return <SpacedComponentObj>
    {children}
  </SpacedComponentObj>
}
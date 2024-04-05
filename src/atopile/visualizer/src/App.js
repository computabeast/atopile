import React from 'react';
import './App.css';

// Example dictionary
const blocksDict = {
  blocks: [
    { id: 'block1', content: 'Block 1' },
    { id: 'block2', content: 'Block 2' },
    { id: 'block3', content: 'Block 3' },
  ],
  links: [
    { source: { block: 'block1', port: 'p1'}, target: { block: 'block2', port: 'p1' }},
    { source: { block: 'block2', port: 'p1'}, target: { block: 'block3', port: 'p1' }},
  ],
};

// Function to get ports connected to a block, agnostic of source or target
const getConnectedPorts = (blockId) => {
  const connectedPorts = [];
  blocksDict.links.forEach(link => {
    if (link.source.block === blockId) {
      connectedPorts.push(link.source.port);
    }
    if (link.target.block === blockId) {
      connectedPorts.push(link.target.port);
    }
  });
  return connectedPorts;
};

// Block component
const Block = ({ block }) => {
    //console.log(block)
  return (
    <div className="block">
      {block.content}
      {/* Additional block details can be rendered here */}
    </div>
  );
};

// BlockWrapper component
const BlockWrapper = ({ block }) => {
    console.log(block)
  return (
    <div className="block-wrapper">
      <Block block={block} />
      {/* Stubbed connection links can be added here if needed */}
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <h1>Blocks Visualizer</h1>
      <div className="blocks-container">
        {blocksDict.blocks.map((block) => (
          <BlockWrapper
            key={block.id}
            block={block}
          />
        ))}
      </div>
    </div>
  );
}

export default App;

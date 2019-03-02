const Emitter = require('events');

const myEmitter = new Emitter();
myEmitter.on('hello', () => {
  console.log('Hello world');
});
myEmitter.emit('hello');

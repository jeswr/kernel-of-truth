/**
 * Unit tests for the FrameNet XML reader.
 * Run: node --test data/onto-framenet/extractor/parse-fn.test.mjs
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { decodeEntities, attrs, cleanDefinition, parseFrameFile, parseFrameRelations } from './parse-fn.mjs';

test('decodeEntities handles named + numeric', () => {
  assert.equal(decodeEntities('a &lt;b&gt; &amp; &#65; &#x42;'), 'a <b> & A B');
});

test('attrs parses double-quoted attributes in any order', () => {
  const a = attrs(' coreType="Core" name="Agent" ID="7" abbrev="Agt"');
  assert.equal(a.name, 'Agent');
  assert.equal(a.coreType, 'Core');
  assert.equal(a.ID, '7');
});

test('cleanDefinition strips markup and cuts at first example', () => {
  const raw = '&lt;def-root&gt;An &lt;fen&gt;Agent&lt;/fen&gt; leaves a &lt;fex name="Theme"&gt;Theme&lt;/fex&gt;.&lt;ex&gt;Carolyn &lt;t&gt;abandoned&lt;/t&gt; her car.&lt;/ex&gt;&lt;/def-root&gt;';
  assert.equal(cleanDefinition(raw), 'An Agent leaves a Theme.');
});

const FRAME_XML = `<?xml version="1.0"?>
<frame name="Test_frame" ID="99">
  <definition>&lt;def-root&gt;A &lt;fen&gt;Doer&lt;/fen&gt; does something.&lt;/def-root&gt;</definition>
  <FE coreType="Core" abbrev="Dr" name="Doer" ID="11">
    <definition>&lt;def-root&gt;The one who acts.&lt;/def-root&gt;</definition>
  </FE>
  <FE coreType="Peripheral" abbrev="Tm" name="Time" ID="12"/>
  <lexUnit POS="V" name="do.v" ID="500"><definition>x</definition></lexUnit>
</frame>`;

test('parseFrameFile: root, FEs (incl self-closing), definitions, LUs', () => {
  const p = parseFrameFile(FRAME_XML);
  assert.equal(p.name, 'Test_frame');
  assert.equal(p.id, 99);
  assert.equal(p.definition, 'A Doer does something.');
  assert.equal(p.fes.length, 2);
  assert.deepEqual(p.fes[0], { name: 'Doer', abbrev: 'Dr', coreType: 'Core', feId: 11 });
  assert.deepEqual(p.fes[1], { name: 'Time', abbrev: 'Tm', coreType: 'Peripheral', feId: 12 });
  assert.equal(p.feDefs.Doer, 'The one who acts.');
  assert.equal(p.lus.length, 1);
  assert.deepEqual(p.lus[0], { name: 'do.v', pos: 'V', luId: 500 });
});

test('parseFrameFile fails closed on FE missing coreType', () => {
  assert.throws(() => parseFrameFile('<frame name="X" ID="1"><FE name="Y" ID="2"></FE></frame>'), /ERR_FN_FE/);
});

const REL_XML = `<frameRelations>
  <frameRelationType name="Inheritance">
    <frameRelation subID="10" supID="20" subFrameName="Child" superFrameName="Parent" ID="500">
      <FERelation subFEName="A" superFEName="A2" ID="1"/>
      <FERelation subFEName="B" superFEName="B2" ID="2"/>
    </frameRelation>
    <frameRelation subID="11" supID="20" subFrameName="Child2" superFrameName="Parent" ID="501"/>
  </frameRelationType>
</frameRelations>`;

test('parseFrameRelations: nested + self-closing, FE mappings, type inheritance', () => {
  const rels = parseFrameRelations(REL_XML);
  assert.equal(rels.length, 2);
  assert.equal(rels[0].relationType, 'Inheritance');
  assert.equal(rels[0].subFrameId, 10);
  assert.equal(rels[0].superFrameId, 20);
  assert.deepEqual(rels[0].feMappings, [{ subFE: 'A', superFE: 'A2' }, { subFE: 'B', superFE: 'B2' }]);
  assert.equal(rels[1].relId, 501);
  assert.equal(rels[1].feMappings.length, 0);
  assert.equal(rels[1].relationType, 'Inheritance');
});

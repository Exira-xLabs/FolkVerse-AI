const paths = {
  up: "M12 19V5m-6 6 6-6 6 6",
  down: "M12 5v14m-6-6 6 6 6-6",
  diagonal: "M6 18 18 6M6 6h12v12",
} as const;

export function ArrowIcon({ direction }: { direction: keyof typeof paths }) {
  return <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d={paths[direction]} /></svg>;
}

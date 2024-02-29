import styles from './page.module.css'
import Link from 'next/link'

export default function Home() {
  return (
    <main className={styles.main}>
      <div className={styles.description}>
        <Link href={"/files"}> Click here to start browsing the videos</Link>
      </div>
    </main>
  );
}
